"""Independent factory No.2 CAD provenance, component measurements and previews.

No Revit launch; no CAD source file changes. STL is tessellated OEM geometry,
not a newly modeled fixture. Neutral preview colours do not certify Clay.
"""
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
import trimesh

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(*parts):
    path = ROOT.joinpath(*parts).resolve()
    if ROOT not in path.parents:
        raise ValueError('Write outside task root')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def render(mesh, direction, filename, caption):
    # Orthographic painter rendering of the original STL triangles. No geometry
    # is smoothed, remeshed, substituted or scaled to fit a nominal dimension.
    forward = np.asarray(direction, dtype=float)
    forward /= np.linalg.norm(forward)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    vertices = np.asarray(mesh.vertices)
    center = (vertices.max(axis=0) + vertices.min(axis=0)) / 2.0
    relative = vertices - center
    flat = np.column_stack((relative @ right, relative @ up))
    low, high = flat.min(axis=0), flat.max(axis=0)
    canvas = (760, 980)
    scale = min((canvas[0] - 110) / (high[0] - low[0]),
                (canvas[1] - 180) / (high[1] - low[1]))
    projected = np.column_stack((canvas[0] / 2 + (flat[:, 0] - (low[0] + high[0]) / 2) * scale,
                                 canvas[1] / 2 - (flat[:, 1] - (low[1] + high[1]) / 2) * scale))
    faces = np.asarray(mesh.faces)
    depth = (relative @ forward)[faces].mean(axis=1)
    normals = np.asarray(mesh.face_normals)
    light = np.array([-0.45, -0.65, 0.8])
    light /= np.linalg.norm(light)
    intensity = 0.40 + 0.60 * np.abs(normals @ light)
    picture = Image.new('RGB', canvas, '#eeeae3')
    draw = ImageDraw.Draw(picture)
    for index in np.argsort(depth)[::-1]:
        rgb = tuple(int(x * intensity[index]) for x in (181, 162, 139))
        draw.polygon([tuple(x) for x in projected[faces[index]]], fill=rgb)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 21)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
    draw.text((28, 24), caption, font=font, fill='#282724')
    draw.text((28, 55), 'Original manufacturer STL • neutral schematic shading', font=small, fill='#514c46')
    draw.text((28, canvas[1] - 55), 'SOURCE CAD REVIEW ONLY — no native Revit QA', font=small, fill='#514c46')
    path = target('previews', filename)
    picture.save(path)
    return str(path)


def main():
    provenance = ROOT / 'sources/premium/schneid_dropbox_probe/SCHNEID_OEM_ARCHIVE_RECEIPT.json'
    source = json.loads(provenance.read_text(encoding='utf-8'))
    archive_path = Path(source['archive_path'])
    assert archive_path.stat().st_size == source['bytes']
    assert sha(archive_path) == source['sha256']
    sources = []
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert len(archive.infolist()) == 19
        assert not [x for x in archive.namelist() if x.lower().endswith('.rfa')]
        for row in source['no2']:
            path = Path(row['local'])
            data = path.read_bytes()
            assert len(data) == row['bytes']
            assert sha(path) == row['sha256']
            assert data == archive.read(row['name'])
            sources.append({'file': str(path), 'bytes': len(data), 'sha256': row['sha256'],
                            'archive_member': row['name'], 'original_byte_identity': True})
    step = ROOT / 'sources/premium/schneid_official_no2/Stucco No.2.stp'
    step_text = step.read_text(encoding='latin1')
    assert 'SI_UNIT(.MILLI.,.METRE.)' in step_text
    stl = ROOT / 'sources/premium/schneid_official_no2/Stucco No.2.stl'
    original_hash = sha(stl)
    mesh = trimesh.load(stl, process=True)
    assert isinstance(mesh, trimesh.Trimesh)
    parts = mesh.split(only_watertight=False)
    components = []
    largest_parts = sorted(parts, key=lambda p: len(p.faces), reverse=True)[:10]
    for i, part in enumerate(largest_parts):
        components.append({'index': i, 'vertices': len(part.vertices), 'triangles': len(part.faces),
                           'minimum_source_xyz': part.bounds[0].tolist(),
                           'maximum_source_xyz': part.bounds[1].tolist(),
                           'extents_source_units': part.extents.tolist(), 'watertight': bool(part.is_watertight)})
    pdf = ROOT / 'sources/premium/originals/SCHNEID_STUCCO_DataSheet.pdf'
    pdf_text = '\n'.join(page.extract_text() for page in PdfReader(pdf).pages)
    assert 'No 2: 10,5 cm x 26,5 cm' in pdf_text
    assert 'No 2 ceiling rose: 14cm x 14 cm' in pdf_text
    text_path = target('qa', 'SCHNEID_DATASHEET_TEXT_R02.txt')
    text_path.write_text(pdf_text, encoding='utf-8')
    previews = [render(mesh, (0, -1, 0), 'SCHNEID_OEM_STL_FRONT_R02.png', 'Schneid Stucco No. 2 — front'),
                render(mesh, (1, -1.4, 0.18), 'SCHNEID_OEM_STL_OBLIQUE_R02.png', 'Schneid Stucco No. 2 — oblique')]
    assert sha(stl) == original_hash
    result = {'status': 'OEM_CAD_BYTES_AND_OFFLINE_MESH_VERIFIED_NOT_NATIVE_RFA',
              'archive': str(archive_path), 'archive_sha256': source['sha256'], 'archive_crc': 'PASS',
              'archive_members': 19, 'rfa_members': 0, 'oem_cad_sources': sources,
              'datasheet': str(pdf), 'datasheet_sha256': sha(pdf),
              'datasheet_text': str(text_path),
              'corrected_manufacturer_dimensions_mm': {'No2_ceramic_body': {'diameter': 105.0, 'height': 265.0},
                                                       'No2_ceiling_rose': {'diameter': 140.0, 'height': 140.0}},
              'source_worker_dimension_correction': 'Earlier 100x265mm body and 105x125mm rose mixed variants; No2 PDF explicitly says 105x265mm and 140x140mm.',
              'stl': str(stl), 'stl_sha256': original_hash,
              'stl_triangle_count': len(mesh.faces), 'stl_bounds_source_units': mesh.bounds.tolist(),
              'stl_extents_source_units': mesh.extents.tolist(),
              'step_declared_units': 'MILLIMETRES',
              'stl_units': 'STL has no intrinsic units; millimetres inferred from same-package STEP and physical component dimensions.',
              'connected_components': components,
              'connected_component_count': len(parts),
              'component_scope': 'Ten largest topological mesh components only; STL disconnected triangles are not semantic CAD parts.',
              'previews': previews, 'neutral_preview_is_not_clay_finish_verification': True,
              'native_import_available_in_revit_2025_api': 'Document.Import(path, ImportOptions3DM, View) returns ElementId; requires optional importer and native execution.',
              'native_import_executed': False, 'native_rfa_created': False,
              'ul_variant': 'OEM CAD has no verified E26 UL socket/certification; exact retailer UL lamp/voltage needs separate confirmation.',
              'release_status': 'REVIEW_NOT_RELEASED'}
    target('qa', 'SCHNEID_OEM_CAD_REVIEW_R02.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'sources': len(sources), 'triangles': len(mesh.faces),
                      'topological_component_count': len(parts),
                      'largest_component_triangle_counts': [x['triangles'] for x in components],
                      'whole_assembly_extents_mm_inferred': mesh.extents.tolist(),
                      'previews': previews}, indent=2))


if __name__ == '__main__':
    main()
