#!/usr/bin/env python

import click
import shapefile

from tqdm import tqdm

@click.group()
def shp_util():
  pass

def _iterRecords(sfreader, title='Reading records'):
  return tqdm(sfreader.iterRecords(), title, unit=' records', total=len(sfreader))

def _iterShapeRecords(sfreader, title='Reading records'):
  return tqdm(sfreader.iterShapeRecords(), title, unit=' records', total=len(sfreader))

@shp_util.command()
@click.argument('shp_file', type=click.Path(dir_okay=False))
@click.argument('field_name', type=str)
def list_field_values(shp_file, field_name):
  """
  List the unique values within a field.
  
  The field identified by FIELD_NAME
  """
  with shapefile.Reader(shp_file) as sf:
    field_values = set()
    for record in _iterRecords(sf):
      fval = record.as_dict().get(field_name)
      if fval is not None:
        field_values.add(fval)
  print('Field values:')
  for idx, fval in enumerate(field_values):
    print('  {:02d}:  {:s}'.format(idx+1, fval))
      
@shp_util.command()
@click.argument('src_shp_file', type=click.Path(dir_okay=False))
@click.argument('dst_shp_file', type=click.Path(dir_okay=False))
@click.argument('field_name')
@click.argument('replacement_pairs', nargs=-1)
def replace_field_values(src_shp_file, dst_shp_file, field_name, replacement_pairs):
  """
  Search and replace of string values within a field.

  The field is identified by FIELD_NAME. REPLACEMENT_PAIRS is expected to be in
  the form of:
  
    OLD1, NEW1, OLD2, NEW2, ..., OLDn, NEWn 
  
  where every occurance of OLD1 is replaced with NEW1 and so forth. This allows
  for many search and replace operations to take place at once avoiding the need
  for temporary intermediate files.
  """
  # ordering matters. Opening dst first means closing it last
  # allowing us to use the same file for destination and source
  with shapefile.Writer(dst_shp_file) as dst:
    with shapefile.Reader(src_shp_file) as src:
      dst.shapeType = src.shapeType

      # [1:] to skip the deletion field
      dst.fields = src.fields[1:]

      replacement_tab = dict()
      for old_val, new_val in zip(replacement_pairs[0::2], replacement_pairs[1::2]):
        replacement_tab[old_val] = new_val

      for shaperec in _iterShapeRecords(src, 'Replacing field values in records'):
        fval = shaperec.record.as_dict().get(field_name)
        replacement = replacement_tab.get(fval)
        if replacement is not None:
          shaperec.record[field_name] = replacement

        dst.shape(shaperec.shape)
        dst.record(*shaperec.record)

@shp_util.command()
@click.argument('shp_file', type=click.Path(dir_okay=False))
def list_fields(shp_file):
  """
  List fields within a shape file.
  """
  with shapefile.Reader(shp_file) as sf:
    for idx, fld in enumerate(sf.fields):
      if idx == 0:
        # ignore the deletion field
        continue
      fname, ftype, flen, fdplaces = fld
      ftype_desc_tab = {
          'C': 'STRING',
          'N': 'NUMBER',
          'F': 'NUMBER',
          'L': 'BOOL',
          'D': 'DATE',
          'M': 'MEMO'
          }

      print('{:03d}: {:16s}\t{:7s}\t{:4d}'.format(idx+1,
                                                fname,
                                                ftype_desc_tab[ftype],
                                                flen))

@shp_util.command()
@click.argument('shp_file', type=click.Path(dir_okay=False))
def info(shp_file):
  """
  Prints metadata about the shp_file.
  """
  with shapefile.Reader(shp_file) as sf:
    print('Shape type:', sf.shapeTypeName)
    print('Number of records:', len(sf))

if __name__ == '__main__':
  import sys
  sys.exit(shp_util())

