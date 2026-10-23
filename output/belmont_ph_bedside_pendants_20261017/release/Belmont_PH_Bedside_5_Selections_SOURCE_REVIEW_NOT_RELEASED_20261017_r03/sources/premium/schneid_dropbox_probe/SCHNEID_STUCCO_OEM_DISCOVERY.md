# Schneid Stucco II OEM CAD discovery — 2026-10-17

**Result: exact Schneid Studio factory Stucco Lamp No.2 geometry was recovered in five native CAD formats.** No manufacturer RFA is present in the official 19-entry ZIP. Preserve factory source geometry and use it for Revit conversion; there is no basis to hand-sculpt a replacement body.

Source: Schneid Studio collection page `https://schneidstudio.com/stucco-collection`, which publishes the official 3D source link to `https://www.dropbox.com/scl/fo/ilg9k5nqeb6od7xbihltv/AJhqNQ6n2bWNgEzoa700D-0?rlkey=ra335kifa8h4anjl5kk6j8yf5&dl=0`.

Read-only inspection of official ZIP (`dl=1`) found:

| Evidence | Result |
| --- | --- |
| HTTP ZIP response | 200; `Content-Length: 186260124` bytes (~177.6 MiB) |
| Requested byte range on direct Dropbox content URL | HTTP 200, not 206; neither `Content-Range` nor `Accept-Ranges` supplied |
| First ZIP local entries, 1 MiB bounded prefix | `/`, `Stucco Lamp No.1/`, `Stucco Lamp No.2/`, `Stucco Lamp No.3/`, `Stucco Lamp No.1/Stucco No.1.3dm` |
| Manufacturer's source format actually demonstrated | Rhino `.3dm` for Stucco Lamp No.1 |
| No.2 exact file member or `.rfa` | Unknown; ZIP's local data uses descriptors, so directory listing cannot be finished from the 1 MiB prefix alone |

The source HTML itself supplies no actual model filenames (all occurrences of filename and file_count are front-end JavaScript identifiers). The ZIP server ignores bounded HTTP Range, so a central-directory listing cannot be retrieved by a tail request. A subsequent one-time full retrieval, justified by confirming the exact No.2 manufacturer directory and 100 GB of free E: drive space, downloaded the original archive and extracted only the five Stucco No.2 CAD members. No Revit family was created and the active Belmont project was untouched.

Original ZIP: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\originals\SCHNEID_Stucco_Share_3D.zip` — 186,260,124 bytes, SHA-256 `b59b212eb37ff7311ac66dff38db282849b15f3d524b0e7d31e7753a7429ad72`. All 19 ZIP entries passed CRC; zero `.rfa` members.

Originals preserved byte-for-byte in `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2`:

| Factory member | Bytes | SHA-256 |
| --- | ---: | --- |
| `Stucco No.2.3dm` | 6,055,200 | `4893770f0fbdedb2b1eccd50d60196f0fef7f01f67af5f8707cab33e6f96be8e` |
| `Stucco No.2.3ds` | 404,343 | `53429869516ba0a9282f5c7539e97f63690a4ade12d43ff2f5d327003dfc9e` |
| `Stucco No.2.skp` | 2,846,121 | `cadc434baf06e91b7155e983046c85d18b03adea198591bc4e247baf41abba7c` |
| `Stucco No.2.stl` | 18,754,541 | `1f06f13b2132cc73050d1a6e843cd9e886dfd92938326ce3f5e74d5f7e04c06a` |
| `Stucco No.2.stp` | 606,439 | `2aa896860b242fbb5c22f34eb6fb7b0dca93b478dcf0cd05753186153f5c968b` |

**Recommendation:** Use exact factory STEP or Rhino geometry as the source for the Stucco II Revit 2025 family. A new family wrapper may still be needed, but its modeled fixture shape should come from these original OEM assets rather than independent reconstruction. The US E26 UL socket and lamp specification must still be checked separately against the factory geometry. Revit native QA remains outstanding.

Canonical readback receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_dropbox_probe\SCHNEID_OEM_ARCHIVE_RECEIPT.json`.

Reproducible probe: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_dropbox_probe\probe_shared_folder.py`. It downloads at most 1 MiB of archive content, discards it, and does not retain any external files.
