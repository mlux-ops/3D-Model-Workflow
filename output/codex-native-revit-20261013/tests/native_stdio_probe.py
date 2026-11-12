"""Exercise real MCP stdio JSON-RPC against the loaded isolated native bridge."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

def main():
    p=argparse.ArgumentParser();p.add_argument('--process-id',type=int,required=True);p.add_argument('--output',required=True);opts=p.parse_args()
    path=Path(__file__).resolve().parents[1]/'controller/native_revit.py'
    process=subprocess.Popen([sys.executable,str(path),'stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    report={'native':True,'transport':'MCP stdio -> authenticated loopback -> ExternalEvent','calls':[]}
    def rpc(method,params):
        request={'jsonrpc':'2.0','id':len(report['calls'])+1,'method':method,'params':params}
        process.stdin.write(json.dumps(request)+'\n');process.stdin.flush();line=process.stdout.readline()
        if not line:raise RuntimeError('MCP server exited without JSON-RPC response')
        response=json.loads(line);report['calls'].append({'request':request,'response':response})
        if 'error' in response:raise RuntimeError(response['error'])
        result=response['result']
        if result.get('isError'):raise RuntimeError(result)
        return result.get('structuredContent',result)
    try:
        init=rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'native-acceptance-probe','version':'1'}})
        tools=rpc('tools/list',{})
        caps=rpc('tools/call',{'name':'native_revit_capabilities','arguments':{}})
        if caps['process_id']!=opts.process_id:raise RuntimeError('Wrong process')
        receipt=rpc('tools/call',{'name':'native_revit_submit','arguments':{'operation':'documents.list','document':{}}})
        result=rpc('tools/call',{'name':'native_revit_wait','arguments':{'operation_id':receipt['operation_id'],'timeout_seconds':30}})
        if result['status']!='completed':raise RuntimeError('Native document query incomplete')
        report.update({'status':'passed','server_identity':init['serverInfo'],'tool_count':len(tools['tools']),'native_process_id':caps['process_id'],'native_operation_id':receipt['operation_id']})
    finally:
        process.stdin.close();process.wait(timeout=10)
        Path(opts.output).write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':main()
