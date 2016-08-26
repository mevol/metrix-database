import sqlite3
import csv
conn = sqlite3.connect('metrix_db.sqlite')
cur = conn.cursor()

stat_name_list = ['anomalouscorrelation','IoverSigma',
'completeness','diffI','lowresolutionlimit','RpimI',
'multiplicity','RmeasIpim','anomalousslope','diffF',
'wilsonbfactor','RmeasI','highresolutionlimit','RpimIpim',
'anomalousmultiplicity','RmergeI','totalobservations','anomalouscompleteness',
'cchalf','totalunique']
pdb_stat_name_list = ['Program',
      'Resolution_Range_High',
      'Resolution_Range_Low',
      'Completeness',
      'Number_of_Reflections',
      'R_Value',
      'Experiment_Type'
      'Date_of_Collection',
      'Synchrotron_(Y/N)',
      'Radiation_Source',
      'Beamline',
      'Wavlength_or_Range',
      'Detector_Type',
      'Detector_Manufacturer',
      'Intensity_Integration_Software',
      'Data_Scaling_Software',
      'Data_Redundancy',
      'R_Merge',
      'R_Sym',
      'I/SIGMA',
      'Solvent_Content',
      'Matthews_Coefficient']

db = [['PDB_id',['pdb_id','data_type']],
      ['PDB_id_Stats', pdb_stat_name_list],
      ['High_Res_Stats', stat_name_list],
      ['Low_Res_Stats', stat_name_list],
      ['Overall_Stats', stat_name_list],
      ['SWEEPS',['wavelength', 'sweep_number']],
      ['Dev_Stats_PDB',['date_time','execution_number']],
      ['Dev_Stats_json', ['date_time','execution_number', 'dials_version']]]

print 'Enter the tables to extract data from. Type "done" when finished.'
print 'Available Tables...'
available_tables = []
for item in db:
    print item[0]
    available_tables.append(item[0])
table_count = 1
to_extract = []
while True:
    table_name = raw_input('Table %s: '% table_count)
    if table_name == 'done':
        if table_count == 1:
            print 'Select at least one table.'
            continue
        else:
            break
    if table_name not in available_tables:
        print 'Invalid name'
        continue
    else:
        to_extract.append([table_name,])
        table_count += 1
print 'Enter the columns to extract data from. Type "done" when finished.'
print 'Type "all" for all columns in that table.'
count = 0
for name in to_extract:
    for item in db:
        table_name = name[0]
        column_list = item[1]
        if table_name == item[0]:
            print 'Available columns for %s are...' % table_name
            for column in column_list:
                print column
            column_count = 1
            while True:
                column_name = raw_input('Column %s: '% column_count)
                if column_name == 'done':
                    if column_count == 1:
                        print 'Select at least one table.'
                        continue
                    else:
                        break
                if column_name == 'all':
                    to_extract[count].append(column_list)
                    break
                if column_name not in column_list:
                    print 'Invalid name'
                    continue
                else:
                    try:
                        to_extract[count][1].append(column_name)
                        column_count += 1
                    except:
                        to_extract[count].append([])
                        to_extract[count][1].append(column_name)
                        column_count += 1
            count += 1

print 'Selected items are...'
for item in to_extract:
    string = item[0] + ':'
    for column in item[1]:
        string += ' ' + column +','
    string = string[:-1]
    print string
while True:
    answer = raw_input('Is this correct? (y/n)')
    if answer.lower() == 'n':
        exit(0)
    elif answer.lower() != 'y':
        print 'Please enter again (y/n)'
        continue
    break

sql_command = str()
for item in to_extract:
    for column in item[1]:
        sql_command += item[0] + '.' + column + ', '

sql_command = sql_command[:-2]
sql_command = 'SELECT ' + sql_command + ' FROM'
sql_command = sql_command + '''
Low_Res_Stats JOIN PDB_id JOIN SWEEPS JOIN High_Res_Stats JOIN
Overall_Stats JOIN Dev_Stats_PDB JOIN Dev_Stats_json JOIN PDB_id_Stats
    ON Low_Res_Stats.sweep_id = SWEEPS.id and SWEEPS.pdb_id_id = PDB_id.id
    and High_Res_Stats.sweep_id = SWEEPS.id and Overall_Stats.sweep_id = SWEEPS.id
    and Dev_Stats_PDB.pdb_id_id = PDB_id.id and Dev_Stats_json.sweep_id = SWEEPS.id
    and PDB_id_Stats.pdb_id_id = PDB_id.id'''

print sql_command

column_headings = []
for item in to_extract:
    for column in item[1]:
        column_headings.append(column)

print column_headings
data = cur.execute(sql_command)
with open('output.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(column_headings)
    writer.writerows(data)
