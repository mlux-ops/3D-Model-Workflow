"""Read CFB streams and stored previews. This does not run or validate Revit.

Pure standard-library compound-file reader for read-only source inspection.
Its output is explicitly distinct from native QA. Source bytes never change.
"""
import hashlib
import json
from pathlib import Path
import struct
from xml.etree import ElementTree as ET

from extract_oem_unchanged import ROOT, out_path


class Compound:
    def __init__(self, data):
        self.data = data
        assert data[:8] == bytes.fromhex('d0cf11e0a1b11ae1')
        self.sector_size = 1 << struct.unpack_from('<H', data, 30)[0]
        self.mini_size = 1 << struct.unpack_from('<H', data, 32)[0]
        assert self.sector_size in (512, 4096)
        assert self.mini_size == 64
        self.cutoff = struct.unpack_from('<I', data, 56)[0]
        fat_count = struct.unpack_from('<I', data, 44)[0]
        difat = list(struct.unpack_from('<109I', data, 76))
        next_difat, difat_count = struct.unpack_from('<II', data, 68)
        for _ in range(difat_count):
            values = struct.unpack('<' + 'I' * (self.sector_size // 4), self.sector(next_difat))
            difat.extend(values[:-1])
            next_difat = values[-1]
        fat_sectors = [x for x in difat if x < 0xfffffffa][:fat_count]
        assert len(fat_sectors) == fat_count
        fat_data = b''.join(self.sector(x) for x in fat_sectors)
        self.fat = struct.unpack('<' + 'I' * (len(fat_data) // 4), fat_data)
        directory = self.regular(struct.unpack_from('<I', data, 48)[0])
        self.entries = []
        for offset in range(0, len(directory), 128):
            row = directory[offset:offset + 128]
            name_len = struct.unpack_from('<H', row, 64)[0]
            name = row[:max(0, name_len - 2)].decode('utf-16-le', errors='replace')
            self.entries.append({'name': name, 'type': row[66],
                                 'start': struct.unpack_from('<I', row, 116)[0],
                                 'size': struct.unpack_from('<Q', row, 120)[0]})
        root = self.entries[0]
        assert root['type'] == 5
        self.mini_stream = self.regular(root['start'])[:root['size']]
        mini_count = struct.unpack_from('<I', data, 64)[0]
        mini_data = self.regular(struct.unpack_from('<I', data, 60)[0])[:mini_count * self.sector_size]
        self.mini_fat = struct.unpack('<' + 'I' * (len(mini_data) // 4), mini_data)

    def sector(self, index):
        start = (index + 1) * self.sector_size
        assert 0 <= index and start + self.sector_size <= len(self.data)
        return self.data[start:start + self.sector_size]

    def chain(self, first, table):
        seen = set()
        current = first
        while current < 0xfffffffa:
            assert current not in seen and current < len(table), 'Invalid CFB chain'
            seen.add(current)
            yield current
            current = table[current]

    def regular(self, first):
        return b''.join(self.sector(i) for i in self.chain(first, self.fat))

    def read(self, entry):
        if entry['size'] < self.cutoff:
            data = b''.join(self.mini_stream[i * self.mini_size:(i + 1) * self.mini_size]
                            for i in self.chain(entry['start'], self.mini_fat))
        else:
            data = self.regular(entry['start'])
        assert len(data) >= entry['size']
        return data[:entry['size']]


def main():
    records = []
    for path in sorted((ROOT / 'families').glob('*.rfa')):
        original = path.read_bytes()
        storage = Compound(original)
        record = {'file': str(path), 'sha256': hashlib.sha256(original).hexdigest(),
                  'scope': 'OFFLINE_STORED_METADATA_ONLY_NOT_NATIVE_QA', 'streams': [],
                  'stored_preview_files': []}
        for entry in storage.entries:
            if entry['type'] != 2:
                continue
            data = storage.read(entry)
            record['streams'].append({'name': entry['name'], 'bytes': len(data)})
            if entry['name'] == 'PartAtom':
                xml = ET.fromstring(data)
                ns = {'a': 'http://www.w3.org/2005/Atom',
                      'p': 'urn:schemas-autodesk-com:partatom'}
                record['saved_family_title'] = xml.findtext('a:title', namespaces=ns)
                record['saved_categories'] = [
                    {'term': cat.findtext('a:term', namespaces=ns),
                     'scheme': cat.findtext('a:scheme', namespaces=ns)}
                    for cat in xml.findall('a:category', ns)]
                record['saved_category'] = next(
                    (x['term'] for x in record['saved_categories']
                     if x['scheme'] == 'adsk:revit:grouping'), None)
                record['saved_product_version'] = xml.findtext('.//p:product-version', namespaces=ns)
                record['saved_host'] = xml.findtext('p:family/a:Host', namespaces=ns)
                record['saved_light_source_flag'] = xml.findtext('.//a:Light_Source', namespaces=ns)
                record['saved_types'] = []
                for part in xml.findall('p:family/p:part', ns):
                    fields = {}
                    for child in part:
                        key = child.tag.split('}')[-1]
                        fields[key] = {'value': child.text,
                                       'units': child.attrib.get('units'),
                                       'parameter_type': child.attrib.get('typeOfParameter')}
                    record['saved_types'].append(fields)
            if 'preview' in entry['name'].lower():
                start = data.find(b'\x89PNG\r\n\x1a\n')
                end = data.find(b'IEND\xaeB`\x82', start)
                if start >= 0 and end >= 0:
                    dest = out_path('previews', 'OEM_STORED_' + path.stem + '.png')
                    png = data[start:end + 8]
                    if dest.exists():
                        assert dest.read_bytes() == png
                    else:
                        dest.write_bytes(png)
                    record['stored_preview_files'].append(str(dest))
        assert path.read_bytes() == original
        records.append(record)
    target = out_path('qa', 'OEM_STORED_METADATA.json')
    target.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps([{'file': x['file'], 'version': x.get('saved_product_version'),
                       'category': x.get('saved_category'), 'host': x.get('saved_host'),
                       'types': [t.get('title', {}).get('value') for t in x.get('saved_types', [])],
                       'stored_preview_count': len(x['stored_preview_files'])}
                      for x in records], indent=2))


if __name__ == '__main__':
    main()
