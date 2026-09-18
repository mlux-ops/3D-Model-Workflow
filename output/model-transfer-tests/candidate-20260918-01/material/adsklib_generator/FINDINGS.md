# .adsklib format findings

Reverse-engineering of Autodesk Revit's `.adsklib` material-library container,
based on three Revit-2025-authored reference libraries: `output/adella/
MSI_Adella_Viso_White_R2025.adsklib`, `output/scandinavian/
Scandinavian_Decor_Grey_R2025.adsklib`, `output/Beige_Fluted_12x24_R2025.adsklib`.
All three are read-only inputs; nothing under `output/adella`, `output/
scandinavian`, `output/beige_fluted_12x24` etc. was modified.

## Container layer (OPC zip)

37 entries. 17 are byte-identical across all three references (every
`Schemas/*.xml` except `cnx.xml`/`core.xml`, `StreamVersionTable`,
`[Content_Types].xml`, `autodesk-design-package.xml`, the 3192-byte
`UnifiedBitmap_png` default thumbnail, several `cnx.xml`). The rest differ
only by substitution of: the package GUID (also the top-level folder
name, appearing as the zip-entry-path prefix and inside several XML
uuid/link-name attributes), the creator GUID, the created/modified
ISO-8601 "...Z" timestamps, and the thumbnail entry's file name.
None of these substitutions change any string's byte length in a way that
requires reframing: GUIDs are always 36 chars, timestamps are always the
fixed YYYY-MM-DDTHH:MM:SSZ format, and XML entries are plain text (not
length-prefixed binary), so a different-length thumbnail name there is
harmless. adsklib_gen.py builds this layer by literal template
substitution over a reference library's own bytes.

## The three AssetData/*.bin streams

### AssetTableOfContents.bin (417 B in every sample)

Pure schema/connection-path listing: for each of the material's 5 "assets"
(PhysMat, its Graphics aspect, its Generic aspect, and the two UnifiedBitmap
texture connections) it stores the connection path string, the child asset's
class name, an int32 pair, and the schema file name. It never contains any
material-specific string (no name, no description, no manufacturer) --
confirmed by it being byte-identical between Adella and Scandinavian despite
those two having completely different name/description/manufacturer text
and lengths. This is the direct evidence that no cross-stream offset table
anywhere depends on any string's length: if one existed, this file would
have had to change.

The one exception found: Beige Fluted's copy differs from the other two in
a single int32 (the Graphics asset's second "count" field: 2 instead of 3).
We could not determine what that count represents (see "Remaining
uncertainties" below) so adsklib_gen.py always emits the Adella/
Scandinavian shape (copied verbatim) for this stream; Fluted's own single
differing int is therefore the one byte range on which a from-scratch
regeneration would differ from the shipped file if it did not reuse
Fluted's own bytes -- which is what build_library()'s template mechanism
does for the round-trip test (see below), so the round-trip result is
still byte-exact.

### DefinitionIteratorProperties.bin (DIP) -- 1648 B in every sample

Holds the CommonSchema definitionIteratorData="true" fields (BaseSchema,
Hidden, UIName, VersionGUID, category, description, keyword, thumbnail) for
each of the 5 assets. Fields that are unset are omitted entirely (no
placeholder), so this stream is fundamentally a concatenation of
self-contained int32-length-prefixed strings and small fixed-width scalars
-- except for one crucial, fully reverse-engineered quirk:

DIP is written through a paginated buffer that flushes every 272 bytes,
at absolute stream offsets pos == 152 (mod 272). Whenever a string
field's content would straddle one of these boundaries, an out-of-band
marker is spliced in at the exact boundary byte, and is NOT counted in
the field's declared 4-byte length:
  - plain "local" string fields (UIName, description): a fixed 8-byte
    marker 02 00 00 00 80 00 00 00.
  - "adp:?asset=/<GUID>/Resources/.../thumbnail/0/<name>" internal
    asset-URI fields: FF FF FF FF + int32(len(remaining bytes)).

This explains everything that first looked like corruption: Adella's own
description field is interrupted mid-word ("cerami" + 8 marker bytes +
"c wall tile...") at absolute offset 152; Beige Fluted's description was
similarly interrupted (and is perfectly readable once the marker is
stripped: "Photo matched beige fluted tile; 12 inch width x 24 inch height;
estimated shallow relief and matte sheen"). We verified this fully by
implementing adsklib_codec.py's encode_plain_field/decode_plain_field/
encode_uri_field_dip/decode_uri_field and round-tripping every UIName
(4x), description (1x) and thumbnail-URI (4x) occurrence in all three
reference libraries byte-for-byte identically (see "Round-trip results").

DIP's total size being exactly 1648 B in all three samples despite very
different name/description/manufacturer lengths is not a fixed-capacity
buffer -- it is this same paginated-marker mechanism (which adds bytes) plus
the "omit unset fields" behavior (which removes them) landing on the same
total by construction of the schema, not by coincidence of padding; once
markers are correctly accounted for, decoding is exact.

### InstanceProperties.bin (IP) -- varies with content (2600 B / 2600 B / 2464 B)

Holds manufacturer, model, url, MaterialClass, color, glossiness,
reflectivity, transparency, refraction index, bump amount, the two
RealWorldScale pairs, and the two EXTERNAL bitmap file-path fields. This
stream's total size visibly tracks content length (Fluted, which lacks a
model/url, is 136 B smaller), confirming it is ordinary concatenation with
no page-boundary quirk for the fields we needed -- except the two
external bitmap-path fields, which use a third, different framing:

Each external bitmap path is split at a fixed CHARACTER offset counted
from the start of that field's own content -- 90 for the first texture
connection in the file (generic_bump_map), 91 for the second
(generic_diffuse) -- regardless of the path's total length or its
absolute position in the file. This is a RELATIVE, per-field rule, not
DIP's ABSOLUTE, whole-stream rule (proven by Beige Fluted: its absolute
marker offsets are 1784/2328, different from Adella/Scandinavian's
1920/2464, while the relative 90/91-from-content-start figure is identical
across all six samples in the three files). The marker is FF FF FF FF +
int32(len(remaining bytes) + 37). The "+37" constant reproduces exactly
across all six samples (two connections x three libraries, remaining-chunk
lengths ranging 8-28 bytes) but its root cause is not understood (see
"Remaining uncertainties").

## Framing verdict: (a) or (b)?

(a) -- genuine Revit format, not patch damage. The decisive evidence:
the identical split-string mechanism (marker at a fixed relative character
offset, "+37" constant, declared length excluding marker overhead) appears
byte-for-byte identically in ALL THREE independently-authored reference
libraries -- including Scandinavian and Beige Fluted, which the brief's own
provenance notes describe as clean Revit 2025 Material Browser output, not
reused/patched containers. A one-off binary patch applied to a single
Adella container could not explain the same quirk recurring, at the same
relative offsets, in two unrelated files.

## Offsets/lengths requiring recomputation

No cross-stream offset table exists anywhere in the format (see the
AssetTableOfContents.bin evidence above). The only recomputation needed is
strictly local to each field being edited:
  - a field's own 4-byte length prefix (must equal its new content's byte
    length, excluding any marker overhead);
  - for DIP's paginated fields, WHICH absolute byte position the field's
    content starts at (since inserting a longer/shorter value upstream in
    the same stream shifts everything after it) -- this in turn changes
    where (or whether) a page-boundary marker needs to be spliced into
    THIS field. We handle this in adsklib_gen._rebuild_dip() by
    processing all edited DIP fields in ascending file order with a running
    byte-shift accumulator, so each field's marker placement is computed
    from its true final position, not its stale template offset. (This was
    the one real bug we hit during implementation -- see "Round-trip
    results".)
  - IP's bitmap-path split is relative to each field's own start, so no
    cross-field shift-tracking is needed there.

## Round-trip results

test_roundtrip.py: for each reference library, extract_params() pulls
every parameter (GUIDs, timestamps, name, description, manufacturer/model/
url, MaterialClass, scalars, both texture paths, RealWorldScale, thumbnail
PNG bytes) and build_library() regenerates the library using that same
file as the "pass-through template" for the handful of InstanceProperties.bin
fields whose exact byte framing we could not fully solve (see next section) --
i.e. every byte that IS understood is independently re-derived through the
codec; only the not-fully-solved fields are asserted equal to the template
rather than re-encoded from scratch.

Result: 37/37 entries byte-identical for Adella, Scandinavian, and Beige
Fluted. zipfile.testzip() is None for all three regenerated files.

This exceeds the "at least Scandinavian and Fluted" target and includes
Adella too -- we found no evidence of the hypothesized hypothesis-(b) patch
damage in Adella once the paginated-marker mechanism was correctly modeled;
Adella round-trips cleanly through the same codec as the other two.

One implementation bug surfaced and was fixed during this work: initially
_rebuild_dip computed each edited field's page-boundary marker using its
ORIGINAL TEMPLATE byte offset, which is correct for the round-trip case
(same GUID/name length in, same out) but wrong once a NEW material name of
different length is substituted (variant's name is 12 characters longer),
because that shifts every field after it. Fixed by re-deriving each field's
true position via a running shift accumulator applied in ascending file
order (see _rebuild_dip's docstring). A second, related bug: the two
"boilerplate" UnifiedBitmap default-thumbnail references embed the package
GUID as a SPLIT string (marker lands inside the GUID text itself, at a
fixed relative offset of 19 chars -- verified identical in all three
references), so a plain global find/replace of the old GUID text can never
match it; those two fields are now decoded, GUID-patched, and re-encoded
like every other edited field rather than being copied verbatim.

## The two M01 deliverables

build_m01.py generates both, using output/adella/... as the read-only
scalar/manufacturer/model/url template (all Adella's own values, as
specified by the task brief) and a fresh bare-hex thumbnail-name scheme
(the brief notes Scandinavian's own real-world use of this scheme, so it is
not a deviation from observed practice) rather than the material-name-
embedded scheme Adella/Fluted happen to use, to avoid the thumbnail URI's
length depending on the material name's length.

- material/baseline/MSI_Adella_Viso_White_1-16_Grout_R2025.adsklib
- material/variant/MSI_Adella_Viso_White_1-8_Grout_R2025.adsklib

verify_m01.py re-reads both files with our own extract_params() and
asserts: zipfile.testzip() is None; the two bitmap paths decode to
exactly the intended run-directory paths; the material name decodes
correctly; RealWorldScale doubles decode to the intended values (within
1e-6, since the Y value legitimately carries ~1e-15-scale floating-point
noise from the same X * (Y/X) recomputation the reference libraries
themselves exhibit -- see below). All checks pass for both files.

## Remaining uncertainties (stated plainly)

- InstanceProperties.bin's manufacturer/model/url region's exact
  byte-level framing was only partially solved. Manufacturer and model
  are ordinary int32-length-prefixed fields and are fully understood. The
  URL field's own length prefix could not be located as a simple 4-byte
  value adjacent to its content in any of the three samples (there is a
  type/flags-looking int32 pair -- observed values 12 and 596 in
  Adella -- immediately before it whose structure we did not decode). This
  is why build_library() only VALIDATES manufacturer/model/url/
  MaterialClass/color/glossiness/reflectivity/transparency/refraction/bump-
  amount against the chosen template rather than independently re-encoding
  them from parameters: for every case this project needed (round-tripping
  the three references, and both M01 outputs, all of which reuse Adella's
  own values for these fields unchanged) this is fully correct, but
  build_library() cannot currently synthesize a NEW manufacturer/model/
  url/color/glossiness value from scratch. Anyone extending this generator
  to vary those fields will need to finish reverse-engineering that region.
- The IP bitmap-path "+37" constant and the DIP "count" ints in
  AssetTableOfContents.bin's per-asset records are empirically reproduced
  but not explained. They were verified byte-exact across all six/three
  respective samples, so we are confident they are correct to reproduce
  as discovered, but we do not know why they take those specific values,
  and cannot predict whether some other material shape (e.g. a texture
  connection type this project never exercised) would need a different
  constant.
- RealWorldScaleY's X * (Y/X) double-precision-noise recomputation is
  reproduced because it exactly matches all three references bit-for-bit,
  but we do not know the real underlying Revit computation that produces
  it (candidates we ruled out: naive feet round-trip, float32 round-trip,
  aspect-ratio-via-float32). For our own new content this noise is
  functionally inert (~1e-15 relative error); we reproduce the pattern
  for consistency but it is not load-bearing.
- Revit itself has not been used to open any of the generated or
  regenerated files. Every check in this project is our own independent
  reader (extract_params, decode_*) plus zipfile.testzip(). Revit is
  the actual authority on whether these files are valid Material Browser
  libraries; that has not been verified here and should be treated as
  unconfirmed until load-tested in Revit.
