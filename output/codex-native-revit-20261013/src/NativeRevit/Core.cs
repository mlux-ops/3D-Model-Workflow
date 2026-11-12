using System.Collections.Concurrent;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;

namespace CodexNativeRevit;

public class RolledBackException(string message, Exception? inner = null) : Exception(message, inner);
public class UnknownCompletionException(string message, Exception? inner = null) : Exception(message, inner);

public static class DocumentRegistry
{
    // Only touched from valid Revit context.
    private static readonly Dictionary<Document, string> Ids = new();
    public static string Id(Document d)
    {
        if (!Ids.TryGetValue(d, out var id)) Ids[d] = id = Guid.NewGuid().ToString();
        return id;
    }
    public static Document Resolve(string id) => Ids.FirstOrDefault(p => p.Value == id && p.Key.IsValidObject).Key
        ?? throw new ArgumentException("Document session ID is closed, stale or from another Revit process.");
    public static object Describe(Document d) => new { session_id = Id(d), title = d.Title, path = d.PathName,
        is_family = d.IsFamilyDocument, is_read_only = d.IsReadOnly, is_modified = d.IsModified, is_workshared = d.IsWorkshared };
}

public static class Util
{
    public static string Get(JsonElement a, string k, string fallback = "") => a.ValueKind == JsonValueKind.Object && a.TryGetProperty(k, out var v) ? v.ToString() : fallback;
    public static double Num(JsonElement a, string k, double fallback = 0) => a.TryGetProperty(k, out var v) ? v.GetDouble() : fallback;
    public static bool Bool(JsonElement a, string k, bool fallback = false) => a.TryGetProperty(k, out var v) ? v.GetBoolean() : fallback;
    public static XYZ Point(JsonElement a) { var v = a.EnumerateArray().Select(x => x.GetDouble()).ToArray(); if (v.Length != 3 || v.Any(x => !double.IsFinite(x))) throw new ArgumentException("Point requires three finite coordinates."); return new XYZ(v[0], v[1], v[2]); }
    public static object Xyz(XYZ p) => new[] {p.X,p.Y,p.Z};
    public static Element Element(Document d, JsonElement a)
    {
        Element? e;
        if (a.ValueKind == JsonValueKind.Object)
        {
            if (Get(a, "document_session_id") != DocumentRegistry.Id(d)) throw new ArgumentException("Element reference must match the target document session.");
            if(!a.TryGetProperty("unique_id",out _) && !a.TryGetProperty("expected_unique_id",out _))throw new ArgumentException("Numeric references require expected_unique_id; prefer UniqueId.");
            e = a.TryGetProperty("unique_id", out var u) ? d.GetElement(u.GetString()) : d.GetElement(new ElementId(a.GetProperty("id").GetInt64()));
            if (a.TryGetProperty("expected_unique_id", out var expected) && e?.UniqueId != expected.GetString()) throw new ArgumentException("ElementId was reused or is stale.");
        }
        else {if(a.ValueKind==JsonValueKind.Number)throw new ArgumentException("Naked numeric ElementId is ambiguous. Use UniqueId or a document-qualified numeric reference with expected_unique_id.");e=d.GetElement(a.GetString());}
        return e is {IsValidObject:true} ? e : throw new ArgumentException("Element does not exist in the target document.");
    }
    public static object Describe(Element e)
    {
        var b = e.get_BoundingBox(null); object? location = e.Location switch {LocationPoint p => new {point=Xyz(p.Point), rotation_radians=p.Rotation}, LocationCurve c => new {start=Xyz(c.Curve.GetEndPoint(0)),end=Xyz(c.Curve.GetEndPoint(1))}, _ => null};
        return new {document_session_id=DocumentRegistry.Id(e.Document),id=e.Id.Value, unique_id=e.UniqueId, name=e.Name, category=e.Category?.Name, category_id=e.Category?.Id.Value, type_id=e.GetTypeId().Value, pinned=e.Pinned, group_id=e.GroupId.Value, level_id=e.LevelId.Value, location, bounds=b==null?null:new{min=Xyz(b.Min),max=Xyz(b.Max)}, host_id=(e as FamilyInstance)?.Host?.Id.Value, family_name=(e as FamilySymbol)?.Family.Name, placement_type=(e as FamilySymbol)?.Family.FamilyPlacementType.ToString(),view_family=(e as ViewFamilyType)?.ViewFamily.ToString(),view_type=(e as View)?.ViewType.ToString(),elevation=(e as Level)?.Elevation};
    }
    public static void Editable(Element e)
    {
        if (e.Pinned) throw new ArgumentException("Pinned element: unpin explicitly before editing.");
        if (e.GroupId != ElementId.InvalidElementId) throw new ArgumentException("Grouped element: group definition edits are not implicit.");
        if (e.Document.IsReadOnly) throw new ArgumentException("Document is read-only.");
        if (e.Document.IsWorkshared && WorksharingUtils.GetCheckoutStatus(e.Document,e.Id)==CheckoutStatus.OwnedByOtherUser) throw new ArgumentException("Element is owned by another user.");
    }
    public static JsonElement Json(object o) => JsonSerializer.SerializeToElement(o);
}

public sealed class Job
{
    public int schema_version {get;set;} = 1;
    public string operation_id {get;set;} = "";
    public string status {get;set;} = "queued";
    public JsonElement request {get;set;}
    public object? result {get;set;}
    public object? error {get;set;}
    public bool cancel_requested {get;set;}
    public string created_utc {get;set;} = DateTime.UtcNow.ToString("O");
    public string? finished_utc {get;set;}
    public double elapsed_ms {get;set;}
    public string transaction_status {get;set;} = "not_started";
}

public sealed class Bridge : IExternalEventHandler, IDisposable
{
    public static Bridge? Instance;
    public static readonly string Root = Environment.GetEnvironmentVariable("CODEX_REVIT_STATE_DIR") ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "CodexNativeRevit");
    readonly ConcurrentQueue<string> queue = new();
    readonly Dictionary<string,Job> jobs = new();
    readonly object gate = new();
    readonly CancellationTokenSource shutdown = new();
    readonly HashSet<string> disposable = new();
    readonly TcpListener listener;
    readonly string token;
    readonly ExternalEvent externalEvent;
    public int Port {get;}
    public Bridge()
    {
        Directory.CreateDirectory(Root); Directory.CreateDirectory(Path.Combine(Root,"jobs"));
        var tokenPath=Path.Combine(Root,"token");
        if (!File.Exists(tokenPath)) File.WriteAllText(tokenPath,Convert.ToHexString(RandomNumberGenerator.GetBytes(32)));
        token=File.ReadAllText(tokenPath).Trim(); if(token.Length<32) throw new InvalidOperationException("Bridge token must be at least 32 characters.");
        foreach(var file in Directory.GetFiles(Path.Combine(Root,"jobs"),"*.json"))
        {
            var j=JsonSerializer.Deserialize<Job>(File.ReadAllText(file)); if(j==null)continue;
            if(j.status is "queued" or "running") {j.status="unknown_completion"; j.error=new{code="PROCESS_RESTART",message="Native state and receipt must be reconciled; this request was not replayed."};}
            jobs[j.operation_id]=j; Persist(j);
        }
        Port=int.Parse(Environment.GetEnvironmentVariable("CODEX_REVIT_PORT")??"49327");
        externalEvent=ExternalEvent.Create(this);
        listener=new TcpListener(IPAddress.Loopback,Port); listener.Start();
        Instance=this; _=Task.Run(Listen);
    }
    void Persist(Job j)
    {
        var dest=Path.Combine(Root,"jobs",j.operation_id+".json"); var tmp=dest+".tmp";
        File.WriteAllText(tmp,JsonSerializer.Serialize(j)); File.Move(tmp,dest,true);
    }
    public void Pulse() { if(!queue.IsEmpty)try{externalEvent.Raise();}catch(Exception e){Log("Dispatch raise: "+e.Message);} }
    async Task Listen()
    {
        while(!shutdown.IsCancellationRequested)
        {
            try {var c=await listener.AcceptTcpClientAsync(shutdown.Token); _=Task.Run(()=>Handle(c));}
            catch(OperationCanceledException){break;} catch(Exception e){Log(e.ToString());}
        }
    }
    public static void Log(string s) => File.AppendAllText(Path.Combine(Root,"diagnostics.log"),DateTime.UtcNow.ToString("O")+" "+s+Environment.NewLine);
    async Task Handle(TcpClient c)
    {
        using(c)
        using(var timeout=CancellationTokenSource.CreateLinkedTokenSource(shutdown.Token))
        {
            timeout.CancelAfter(TimeSpan.FromSeconds(15)); var stream=c.GetStream();
            try
            {
                var bytes=new List<byte>(); var one=new byte[1];
                while(bytes.Count<16384)
                {
                    if(await stream.ReadAsync(one,timeout.Token)==0)return; bytes.Add(one[0]);
                    if(bytes.Count>=4 && bytes.TakeLast(4).SequenceEqual(new byte[]{13,10,13,10}))break;
                }
                var headers=Encoding.ASCII.GetString(bytes.ToArray()).Split("\r\n"); var first=headers[0].Split(' ');
                if(first.Length!=3)throw new ArgumentException("Malformed HTTP request.");
                var h=headers.Skip(1).Where(x=>x.Contains(':')).ToDictionary(x=>x[..x.IndexOf(':')].Trim(),x=>x[(x.IndexOf(':')+1)..].Trim(),StringComparer.OrdinalIgnoreCase);
                int status=200; object payload;
                var auth=h.GetValueOrDefault("Authorization",""); var expected="Bearer "+token;
                if(!CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(auth),Encoding.UTF8.GetBytes(expected))) {status=401;payload=new{error="AUTH_REQUIRED"};}
                else if(h.ContainsKey("Transfer-Encoding")) {status=400;payload=new{error="Chunked requests unsupported"};}
                else
                {
                    int length=int.Parse(h.GetValueOrDefault("Content-Length","0")); if(length<0||length>2_000_000)throw new ArgumentException("Body exceeds 2 MB.");
                    var body=new byte[length]; await stream.ReadExactlyAsync(body,timeout.Token);
                    (status,payload)=Route(first[0],first[1],body);
                }
                var data=JsonSerializer.SerializeToUtf8Bytes(payload); var response=Encoding.ASCII.GetBytes($"HTTP/1.1 {status} Response\r\nContent-Type: application/json\r\nContent-Length: {data.Length}\r\nConnection: close\r\n\r\n");
                await stream.WriteAsync(response,timeout.Token); await stream.WriteAsync(data,timeout.Token);
            }
            catch(Exception e) { Log("HTTP "+e.Message); try {var status=e is ArgumentException or JsonException or KeyNotFoundException?400:500;var data=Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new{error=e.Message,recovery="Query original operation_id; infrastructure failures may follow durable acceptance."})); await stream.WriteAsync(Encoding.ASCII.GetBytes($"HTTP/1.1 {status} Error\r\nContent-Length: {data.Length}\r\nConnection: close\r\n\r\n")); await stream.WriteAsync(data);}catch{} }
        }
    }
    (int,object) Route(string method,string path,byte[] body)
    {
        lock(gate)
        {
            if(method=="GET" && path=="/v1/capabilities") return(200,new{schema_version=1,identity="codex-native-revit-2025",process_id=Environment.ProcessId,operations=Operations.Names,family_operations=FamilyOperations.Names,units="Internal feet; angle radians; sheet coordinates feet",flexible_execution="trusted compiled plugins; disabled by default",max_body_bytes=2_000_000});
            if(method=="POST" && path=="/v1/jobs")
            {
                var r=JsonDocument.Parse(body).RootElement.Clone(); if(r.GetProperty("schema_version").GetInt32()!=1)throw new ArgumentException("Unsupported schema_version.");
                var id=r.GetProperty("operation_id").GetString()!; if(!Guid.TryParseExact(id,"D",out _))throw new ArgumentException("operation_id must be UUID in D format.");
                if(jobs.TryGetValue(id,out var previous)) return previous.request.GetRawText()==r.GetRawText()?(200,Util.Json(previous)):(409,new{error="OPERATION_ID_CONFLICT",operation_id=id});
                var j=new Job{operation_id=id,request=r}; jobs[id]=j;
                try{Persist(j);}catch(Exception e){j.status="failed";j.error=new{code="JOURNAL_FAILURE",message="Request was not enqueued: "+e.Message};throw;}
                queue.Enqueue(id);Pulse();return(202,Util.Json(j));
            }
            var parts=path.Split('/',StringSplitOptions.RemoveEmptyEntries);
            if(parts.Length>=3 && parts[0]=="v1" && parts[1]=="jobs" && jobs.TryGetValue(parts[2],out var job))
            {
                if(method=="GET" && parts.Length==3)return(200,Util.Json(job));
                if(method=="POST" && parts.Length==4 && parts[3]=="cancel")
                {
                    job.cancel_requested=true;
                    if(job.status=="queued") {job.status="cancelled";job.finished_utc=DateTime.UtcNow.ToString("O");} Persist(job);return(200,Util.Json(job));
                }
            }
            return(404,new{error="NOT_FOUND"});
        }
    }
    public void Execute(UIApplication app)
    {
        if(!queue.TryDequeue(out var id))return;
        Job j; lock(gate){j=jobs[id];if(j.status!="queued")return;j.status="running";Persist(j);}
        var clock=Stopwatch.StartNew();
        try
        {
            var r=j.request; var op=Util.Get(r,"operation"); var a=r.TryGetProperty("arguments",out var args)?args:Util.Json(new{});
            Document? d=null;
            foreach(Document open in app.Application.Documents)DocumentRegistry.Id(open);
            if(r.TryGetProperty("document",out var target) && target.ValueKind==JsonValueKind.Object && target.TryGetProperty("session_id",out _))
            {
                d=DocumentRegistry.Resolve(Util.Get(target,"session_id"));
                if(target.TryGetProperty("path",out var p) && !string.Equals(d.PathName,p.GetString(),StringComparison.OrdinalIgnoreCase))throw new ArgumentException("Target document path changed.");
            }
            var pre=r.TryGetProperty("preconditions",out var pr)?pr:Util.Json(new{});
            foreach(var condition in pre.EnumerateObject())if(condition.Name is not "expected_title" and not "is_family" and not "allow_existing_document")throw new ArgumentException("Unsupported precondition: "+condition.Name);
            if(d!=null && pre.TryGetProperty("expected_title",out var title) && d.Title!=title.GetString())throw new ArgumentException("Document title precondition failed.");
            if(d!=null && pre.TryGetProperty("is_family",out var family) && d.IsFamilyDocument!=family.GetBoolean())throw new ArgumentException("Document kind precondition failed.");
            if(Operations.Mutates(op) && d!=null && !disposable.Contains(DocumentRegistry.Id(d)) && !Util.Bool(pre,"allow_existing_document"))throw new ArgumentException("Existing document mutation requires explicit preconditions.allow_existing_document=true.");
            if(j.cancel_requested) throw new OperationCanceledException();
            object result;
            if(op=="document.create")
            {
                d=app.Application.NewProjectDocument(Util.Get(a,"template")); disposable.Add(DocumentRegistry.Id(d));result=DocumentRegistry.Describe(d);
            }
            else if(FamilyOperations.Handles(op))
            {
                result=FamilyOperations.Execute(app,d,op,a);
                if(op is "family.create" or "family.edit") {var el=Util.Json(result); if(el.TryGetProperty("session_id",out var sid))disposable.Add(sid.GetString()!);}
            }
            else if(Operations.Mutates(op) && !Operations.Lifecycle(op))
            {
                if(d==null)throw new ArgumentException("Mutation requires explicit document.");
                using var tx=new Transaction(d,"Codex "+op+" "+id[..8]);
                if(tx.Start()!=TransactionStatus.Started)throw new InvalidOperationException("Transaction did not start.");
                lock(gate)j.transaction_status="started";
                tx.SetFailureHandlingOptions(tx.GetFailureHandlingOptions().SetFailuresPreprocessor(new Failures()).SetClearAfterRollback(true));
                try
                {
                    result=Operations.Execute(app,d,op,a);d.Regenerate();
                    if(j.cancel_requested)throw new OperationCanceledException("Cancelled at pre-commit boundary.");
                }
                catch(Exception e)
                {
                    var rollback=tx.GetStatus()==TransactionStatus.Started?tx.RollBack():tx.GetStatus();
                    lock(gate)j.transaction_status=rollback.ToString().ToLowerInvariant();
                    if(rollback!=TransactionStatus.RolledBack)throw new UnknownCompletionException("Rollback not confirmed: "+rollback,e);
                    if(e is OperationCanceledException)throw;
                    throw new RolledBackException(e.Message,e);
                }
                TransactionStatus status;
                try{status=tx.Commit();}catch(Exception e){status=tx.GetStatus();lock(gate)j.transaction_status=status.ToString().ToLowerInvariant();if(status==TransactionStatus.RolledBack)throw new RolledBackException(e.Message,e);throw new UnknownCompletionException("Commit threw; native transaction status is "+status,e);}
                lock(gate)j.transaction_status=status.ToString().ToLowerInvariant();
                if(status==TransactionStatus.RolledBack)throw new RolledBackException("Transaction commit rolled back.");
                if(status!=TransactionStatus.Committed)throw new UnknownCompletionException("Transaction commit returned "+status);
                try{result=Util.Json(new{data=result,transaction_status="committed",actual_elements=Readbacks(d,Util.Json(result)),warnings=d.GetWarnings().Select(w=>new{description=w.GetDescriptionText(),element_ids=w.GetFailingElements().Select(x=>x.Value).ToArray()}).ToArray()});}
                catch(Exception e){throw new UnknownCompletionException("Transaction committed but result readback failed. Reconcile native state.",e);}
            }
            else result=Operations.Execute(app,d,op,a);
            // Detach all native objects and deferred enumerables before leaving valid API context.
            var detached=Util.Json(result);
            lock(gate){j.result=detached;j.status="completed";if(detached.ValueKind==JsonValueKind.Object && detached.TryGetProperty("transaction_status",out var ts))j.transaction_status=ts.GetString()!;}
        }
        catch(OperationCanceledException e){lock(gate){j.status="cancelled";j.error=new{code="CANCELLED",message=e.Message};}}
        catch(Exception e){lock(gate){j.status=e is UnknownCompletionException?"unknown_completion":e is RolledBackException?"rolled_back":"failed";j.error=new{code=e.GetType().Name,message=e.Message,details=e.InnerException?.Message};}Log(id+" "+e);}
        finally {lock(gate){j.elapsed_ms=clock.Elapsed.TotalMilliseconds;j.finished_utc=DateTime.UtcNow.ToString("O");Persist(j);}}
    }
    public string GetName()=>"Codex Native Revit serialized dispatcher";
    static object[] Readbacks(Document d,JsonElement result)
    {
        var uids=new HashSet<string>();
        void Walk(JsonElement e)
        {
            if(e.ValueKind==JsonValueKind.Array){foreach(var item in e.EnumerateArray())Walk(item);}
            if(e.ValueKind!=JsonValueKind.Object)return;
            if(e.TryGetProperty("document_session_id",out var sid) && sid.GetString()==DocumentRegistry.Id(d) && e.TryGetProperty("unique_id",out var uid))uids.Add(uid.GetString()!);
            foreach(var item in e.EnumerateObject())Walk(item.Value);
        }
        Walk(result);return uids.Select(u=>d.GetElement(u)).Where(e=>e!=null&&e.IsValidObject).Select(Util.Describe).ToArray();
    }
    public void Dispose(){shutdown.Cancel();listener.Stop();externalEvent.Dispose();Instance=null;}
    sealed class Failures:IFailuresPreprocessor
    {
        public FailureProcessingResult PreprocessFailures(FailuresAccessor a) => a.GetFailureMessages().Any(f=>f.GetSeverity()==FailureSeverity.Error)?FailureProcessingResult.ProceedWithRollBack:FailureProcessingResult.Continue;
    }
}

public class App : IExternalApplication
{
    Bridge? bridge;
    public Result OnStartup(UIControlledApplication app)
    {
        try {bridge=new Bridge();app.Idling+=OnIdling;return Result.Succeeded;}
        catch(Exception e){try{Bridge.Log(e.ToString());}catch{}return Result.Failed;}
    }
    void OnIdling(object? sender,Autodesk.Revit.UI.Events.IdlingEventArgs e)=>bridge?.Pulse();
    public Result OnShutdown(UIControlledApplication app){app.Idling-=OnIdling;bridge?.Dispose();return Result.Succeeded;}
}
