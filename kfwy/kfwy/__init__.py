import membrane_potential
import H2O2
import NADHRedox
import merge_mp
import merge_nadh
import merge_h2o2

tool_list = ['Membrane Potential', 'NADH Redox', 'H2O2', 'Merge MP', 'Merge NADH Redox', 'Merge H2O2']
NUM_TOOL = 0

# Retrieves assay type from user
print('\nAssay List:')
for i in range(len(tool_list)):
    print('\t{}) {}'.format(i+1, tool_list[i]))
print('To select a tool, enter the number it corresponds with in the list.\n\n[Example] When selecting Membrane Potential\n> Select tool: 1')
print('-----------------------------------------------')

while True:	
    try:
        NUM_ASSAY = int(raw_input('Select tool: '))
        break
    except ValueError:
        print('\n[Error]: Please enter a valid number.\n')

if(NUM_ASSAY == 1):
    membrane_potential.main()
elif(NUM_ASSAY == 2):
    NADHRedox.main()
elif(NUM_ASSAY == 3):
    H2O2.main()
elif(NUM_ASSAY == 4):
    merge_mp.main()
elif(NUM_ASSAY == 5):
    merge_nadh.main()
elif(NUM_ASSAY == 6):
    merge_h2o2.main()
    