# -*- coding: utf-8 -*-
from __future__ import division

class PDBParser(object):
  '''
  A class to parse a pdb file

  '''
  def __init__(self, handle):
    '''
    Initialise the class with the handle

    '''
    self.handle = handle

  def add_entry(self, pdb_id, filename):
    '''
    Add the pdb entry to the database

    '''
    import datetime

    def statRetreive(line):
        try:
          pos = [i for i,x in enumerate(line) if x == ':']
          return ' '.join(line[-1:])
        except:
          print 'Could not find data for: %s' % (line)

    def lineCheck(wordlist, line):
        wordlist = wordlist.split()
        return set(wordlist).issubset(line)

    def printLine(line):
        print ' '.join(line)

    # Get the sqlite cursor
    cur = self.handle.cursor()

    # Read the pdb file
    print 'Reading: %s for pdb id: %s' % (filename, pdb_id)
    with open(filename) as infile:

      atom_num = 'NaN'
      wilson_b = 'NaN'
      method = 'NaN'
      solvent_content = 'NaN'

      # Assigns required statistics to their pointers
      for line in infile.readlines():
        line = line.split()

        if 'BIN' in line:
            continue
        if line[0] == 'HEADER':
          assert pdb_id == line[-1], "Expected %s, got %s" % (pdb_id, line[-1])
        if lineCheck('REMARK 3 PROGRAM',line):
          program = statRetreive(line)
        if lineCheck('REMARK 3 RESOLUTION RANGE HIGH (ANGSTROMS)',line):
          resolution_range_high = statRetreive(line)
        if lineCheck('REMARK 3 RESOLUTION RANGE LOW (ANGSTROMS)',line):
          resolution_range_low = statRetreive(line)
        if lineCheck('REMARK 3 COMPLETENESS FOR RANGE', line):
          completeness = statRetreive(line)
        if lineCheck('REMARK 3 NUMBER OF REFLECTIONS',line):
          number_of_reflections = statRetreive(line)
        if lineCheck('REMARK 3 R VALUE (WORKING SET)',line):
          if '+' in line:
            continue
          else:
            r_value = statRetreive(line)
        if lineCheck('REMARK 3 FREE R VALUE', line):
          if 'TEST' in line or 'ESU' in line:
            continue
          else:
            free_r_value = statRetreive(line)
        if lineCheck('REMARK 3 PROTEIN ATOMS', line):
          atom_num = statRetreive(line)
        if lineCheck('REMARK 3 FROM WILSON PLOT (A**2)', line):
          wilson_b = statRetreive(line)
        if lineCheck('REMARK 200 DATE OF DATA COLLECTION', line):
          date_of_collection = statRetreive(line)
        if lineCheck('REMARK 200 SYNCHROTRON', line):
          synchrotron = statRetreive(line)
        if lineCheck('REMARK 200  RADIATION SOURCE               :', line):
          radiation_source = statRetreive(line)
        if lineCheck('REMARK 200 BEAMLINE', line):
          beamline = statRetreive(line)
        if lineCheck('REMARK 200  WAVELENGTH OR RANGE        (A) ', line):
          wavelength_or_range = statRetreive(line)
        if lineCheck('REMARK 200 DETECTOR TYPE', line):
          detector_type = statRetreive(line)
        if lineCheck('REMARK 200 DETECTOR MANUFACTURER', line):
          detector_manufacturer = statRetreive(line)
        if lineCheck('REMARK 200  INTENSITY-INTEGRATION SOFTWARE :', line):
          intensity_software = statRetreive(line)
        if lineCheck('REMARK 200 DATA SCALING SOFTWARE', line):
          data_scaling_software = statRetreive(line)
        if lineCheck('REMARK 200 DATA REDUNDANCY', line):
          data_redundancy = statRetreive(line)
        if lineCheck('REMARK 200 R MERGE', line):
          r_merge = statRetreive(line)
        if lineCheck('REMARK 200 R SYM', line):
          r_sym = statRetreive(line)
        if lineCheck('REMARK 200 <I/SIGMA(I)> FOR THE DATA', line):
          i_over_sigma = statRetreive(line)
        if lineCheck('REMARK 200 METHOD USED TO DETERMINE THE STRUCTURE:', line):
          method = statRetreive(line)
        if lineCheck('REMARK 280 SOLVENT CONTENT, VS', line):
          solvent_content = line[len(line) - 1]
        if lineCheck('REMARK 280 MATTHEWS COEFFICIENT, VM', line):
          matthews_coefficient = line[len(line) - 1]
        if line[0] == 'CRYST1':
            info = line[1:]


      # What to do if this script cannot find the variable?
      # - Could add initialised variables to a list?
      # - Then add them to the dictionary
      # - Main issue seems to be with solvent_content
      
      pdb_data = {
        'Program'                        : program,
        'Resolution_Range_High'          : resolution_range_high,
        'Resolution_Range_Low'           : resolution_range_low,
        'Completeness'                   : completeness,
        'Number_of_Reflections'          : number_of_reflections,
        'R_Value'                        : r_value,
        'R_free'                         : free_r_value,
        'Num_Atoms'                      : atom_num,
        'Wilson_B'                       : wilson_b,
        'Date_of_Collection'             : date_of_collection,
        'Synchrotron_(Y/N)'              : synchrotron,
        'Radiation_Source'               : radiation_source,
        'Beamline'                       : beamline,
        'Wavelength_or_Range'            : wavelength_or_range,
        'Detector_Type'                  : detector_type,
        'Detector_Manufacturer'          : detector_manufacturer,
        'Intensity_Integration_Software' : intensity_software,
        'Data_Scaling_Software'          : data_scaling_software,
        'Data_Redundancy'                : data_redundancy,
        'R_Merge'                        : r_merge,
        'R_Sym'                          : r_sym,
        'I/SIGMA'                        : i_over_sigma,
        'Phasing_method'                 : method,
        'Solvent_Content'                : solvent_content, 
        'Matthews_Coefficient'           : matthews_coefficient
      }

      # Inserts acquired information into relevant tables
      # Inserts pdb_id
      cur.executescript( '''
        INSERT OR IGNORE INTO PDB_id
        (pdb_id) VALUES ("%s");
        INSERT OR IGNORE INTO PDB_id_Stats
        (pdb_id_id)  SELECT id FROM PDB_id
        WHERE PDB_id.pdb_id="%s";
      ''' % (pdb_id, pdb_id))

      cur.execute('''
        SELECT id FROM PDB_id WHERE pdb_id="%s"
      ''' % (pdb_id))
      pdb_pk = (cur.fetchone())[0]

      # Inserts pdb reference statistics
      # Adds necessary columns
      for data_names in pdb_data.keys():
        try:
          cur.executescript('''
            ALTER TABLE PDB_id_Stats ADD "%s" TEXT
          ''' % (data_names))
        except:
          pass
      items = len(pdb_data)

      for data in pdb_data:
          cur.execute('''
            UPDATE PDB_id_Stats SET "%s" = "%s"
            WHERE pdb_id_id = "%s"
          ''' % (data, pdb_data[data], pdb_pk ))

      cur.execute('''
        INSERT INTO Dev_Stats_PDB (pdb_id_id) VALUES (%s)
      ''' % (pdb_pk))
      cur.execute('''
        UPDATE Dev_Stats_PDB SET date_time = "%s"
        WHERE Dev_Stats_PDB.pdb_id_id= "%s"
      ''' % (str(datetime.datetime.today()), pdb_pk))

      cur.execute('''
        SELECT pdb_id_id FROM Dev_Stats_PDB WHERE Dev_Stats_PDB.pdb_id_id=%s
      ''' % (pdb_pk))
      number_of_executions = len(cur.fetchall())
      cur.execute('''
        UPDATE Dev_Stats_PDB SET execution_number = "%s"
        WHERE Dev_Stats_PDB.pdb_id_id="%s" ''' % (
      number_of_executions, pdb_pk))
      self.handle.commit()
