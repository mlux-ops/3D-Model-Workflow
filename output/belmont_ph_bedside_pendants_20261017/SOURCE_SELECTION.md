# Current source selection and provenance — R03, REVIEW_NOT_RELEASED

All four OEM RFA copies retain original archive member names and bytes. Manufacturer source/type presence is separate from exact finish, voltage/dimming, native scale and host QA.

## 41411-BG

Original family: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\41411 - Jarvis.rfa`.
Original/package SHA-256: `043b83525d3b4be656160d6ef0187a78d067eae0d9eec4a2e720a292b055deed`.
Archive: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\REVIT-41411-Jarvis.zip`.
Archive SHA-256: `46aee4e61c4f539f0e484cca5056c720afe35a1a0a422d5f8c7e1b4679a2fc1a`.
Factory download URL: https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-41411-Jarvis.zip

Stored types: `41411-BK`, `41411-BN`, `41411-CH`, `41411-VB`, `41411-WH`.

FINISH_HOLD: stored types BK, BN, CH, VB and WH; BG absent. Do not substitute VB for BG.

Decision: include unchanged source only; no exact selected-variant approval or native technical pass.

## 402401BG-LED

Original family: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\402401LED-Malabar.rfa`.
Original/package SHA-256: `e580b3bc8d59392eb21a39ce409635fb0efed3a05f8339f3ac6e8f38aeef24da`.
Archive: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\REVIT-402401-LED-Malabar.zip`.
Archive SHA-256: `7419de3103fa92f9a0849242a3a7ea4757243aae813a5f0e45469b5aad521592`.
Factory download URL: https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-402401-LED-Malabar.zip

Stored types: `4024014BG-LED`, `402401CH-LED`.

FINISH_HOLD: literal saved type 4024014BG-LED contains an extra 4; actual metal/optic assignments unverified. PHOTOMETRY_HOLD: saved file names Mina 401214WH-LED, not Malabar.

Decision: include unchanged source only; no exact selected-variant approval or native technical pass.

## 494502M-GD

Original family: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\494502M-Milca.rfa`.
Original/package SHA-256: `a99377ec2f1a7204f336951bd92494889419d057ef420add2abf24606376f540`.
Archive: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\REVIT-494502M-Milca.zip`.
Archive SHA-256: `5cb3b71f16355b46fd929435f904d1fc92512d5f4755efe44baabf960d38a658`.
Factory download URL: https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-494502M-Milca.zip

Stored types: `494502M-GD`, `494502M-BK`, `494502M-BN`, `494502M-GY`.

STORED_TYPE_MATCH: exact 494502M-GD with 494502_GD_FINISH; native geometry/finish QA pending.

Decision: include unchanged source only; no exact selected-variant approval or native technical pass.

## A691-474-37-27K

Original family: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\MARSET_Interior-Lighting-Fixture-Suspended_Dipping-Light.rfa`.
Original/package SHA-256: `c5b1206598b104caa8e1f23a555129c6c86f05e707f58ff1dc091c6bf23a6a74`.
Archive: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\originals\MARSET_Dipping_Light_S_BIM_Link_Check.zip`.
Archive SHA-256: `9e409695020aae2f9199d40972e38953446c612c929a0c1d08bdc89ee960f614`.
Factory download URL: https://www.marset.com/wp-content/uploads/lamparas/sobremesa/dipping-light-sobremesa/MARSET_Dipping-Light-S_Indoor-Lighting_RFA.zip

Stored types: `A691-260`, `A691-241`, `A691-242`, `A691-243`, `A691-244`, `A691-250`, `A691-251`, `A691-252`, `A691-253`, `A691-254`, `A691-240`, `A691-261`, `A691-262`, `A691-263`, `A691-264`, `A691-270`, `A691-271`, `A691-272`, `A691-273`, `A691-274`, `A691-280`, `A691-281`, `A691-282`, `A691-283`, `A691-284`, `A691-290`, `A691-291`, `A691-292`, `A691-293`, `A691-294`.

VARIANT_HOLD: 30 legacy types; no exact requested SKU, no Cream material or 0-10V type. 13 cm types show 13.5 cm diameter, Triac or 24V, White/Blue/Green/Amber/Pink; stored canopy 4.8 cm diameter x 13.4 cm height differs from current US 0-10V canopy.

Decision: include unchanged source only; no exact selected-variant approval or native technical pass.

## STUCCO-II-CLAY-UL

Official source: https://schneidstudio.com/stucco-collection ; https://schneidstudio.com/s/STUCCO_DataSheet.pdf .

Recovered full source archive: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\originals\SCHNEID_Stucco_Share_3D.zip`; SHA-256 `b59b212eb37ff7311ac66dff38db282849b15f3d524b0e7d31e7753a7429ad72`.
19 entries, all source CRCs pass, zero RFA members. The earlier bounded download failure is resolved by the source worker’s one-time full acquisition; original failed-download manifest is retained as history.

Confirmed No.2 manufacturer dimensions: body D105 × H265 mm; ceiling rose D140 × H140 mm. The sheet’s E27/220–240V specification is not proof of the selected US E26 UL variant. CAD includes bulb and suspension; exact UL internal hardware, clay rendering and lamp data remain unverified.

Original CAD: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2\Stucco No.2.3dm`; SHA-256 `4893770f0fbdedb2b1eccd50d60196f0fef7f01f67af5f8707cab33e6f96be8e`.

Original CAD: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2\Stucco No.2.3ds`; SHA-256 `53429869516ba0a1a9282f5c7539e97f63690a4ade12d43ff2f5d327003dfc9e`.

Original CAD: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2\Stucco No.2.skp`; SHA-256 `cadc434baf06e91b7155e983046c85d18b03adea198591bc4e247baf41abba7c`.

Original CAD: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2\Stucco No.2.stl`; SHA-256 `1f06f13b2132cc73050d1a6e843cd9e886dfd92938326ce3f5e74d5f7e04c06a`.

Original CAD: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2\Stucco No.2.stp`; SHA-256 `2aa896860b242fbb5c22f34eb6fb7b0dca93b478dcf0cd05753186153f5c968b`.

Decision: preserve source geometry; build only a new Stucco native family wrapper after runtime recovery. Use supported Rhino/STEP import and verify actual source units, geometry, materials, emitter and ceiling placement. No synthetic replacement geometry or empty RFA is delivered.

Native status: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\NATIVE_RECOVERY_STATUS_R02.json`.
Detailed type/finish/photometry audit: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\OEM_VARIANT_RESOLUTION.md`.
Source CAD measurements/previews: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\SCHNEID_OEM_CAD_REVIEW_R02.json`.
