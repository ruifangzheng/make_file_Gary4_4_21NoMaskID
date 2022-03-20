import os 
import shutil
import json
import requests
import subprocess
import hashlib


#get the file name and study informarion
file_name = input("please enter the file name: ")
study_name = file_name #input ("please enter the name of the study: ")
study_name_short = file_name #input ("please enter the short name of the study: ")
study_description = "mutation study" #input ("please enter the description of the study: ")
profile_description = "mutation profile from GO" #input ("please enter the mutation profile description: ")
#tumor_type = "hematopoietic" #input("Please enter tumor type, answer solid or hematopoietic: ")

#This function is to get the disease of the sample
def get_disease(str):
    r = requests.get("https://patheuhmollabserv2.eushc.org:12443/clinical-app/api/orders/?order_id=" + str, auth=('xxxxxx', 'xxxxxxx'))
    data = json.loads(r.text)
    #print(data[0]['diseases'][0]['display'])
    if len(data) != 0:
        return data[0]['diseases'][0]['display']
    else:
        return "Not provided"
        
 
 
#os.system('./case_attributes_by_acc_no.sh MD21-337') get patient ID and collection date
def get_collection_date_patientID (str):
    date_ID = subprocess.Popen("./case_attributes_by_acc_no.sh " + str, shell=True, stdout=subprocess.PIPE)
    date_ID_text = date_ID.stdout.read().decode('utf-8')
    if len(date_ID_text) != 0:
        return date_ID_text
    else:
        return "null" + '\t' + "null" + '\t' + "null" + '\n'
    
    
# Directory 
directory_temp= "temp"
directory_case_lists = "case_lists"
directory_ID_lookup = "ID_lookup"
  
# Parent Directory 
parent_dir = os.getcwd()
  
# create new directories, temp and case_lists
path_temp = os.path.join(parent_dir, directory_temp) 
path_case_lists = os.path.join(parent_dir, directory_case_lists)
path_ID_lookup = os.path.join(parent_dir, directory_ID_lookup)

isdir_temp = os.path.isdir (path_temp)
if isdir_temp == False:
    os.mkdir(path_temp)   

isdir_case_lists = os.path.isdir(path_case_lists)
if isdir_case_lists == False: 
    os.mkdir(path_case_lists)
    
isdir_ID_lookup = os.path.isdir(path_ID_lookup)
if isdir_ID_lookup == False: 
    os.mkdir(path_ID_lookup)
    

no_name_list = open (path_temp + '/' + "no_name_patient_id.txt", "w+") #create a file containing patient no name id  
mutation_maf = open("data_mutations_extended.txt", "w+") #create a maf file with no name id
no_duplicate_list = open(path_temp + '/' + "no_duplicate_id.txt", "w+") #create a file containing no dulpicate id
ID_lookup_table = open(path_ID_lookup + '/' + "ID_lookup_table.txt", "a+") # create a file containing the original ID and hashed ID

#get the position of the patient sample barcode
first_line = [] #first line of the file
more_lines = [] #additional lines in the file
n=0 #position of the barcode
m=0 #items in the underscore list
with open(file_name + ".txt", "r+") as file_case_list:    
    line_contents = file_case_list.readline()
    first_line = line_contents.split('\t')   
n = first_line.index("Tumor_Sample_Barcode")
 
#get the string of patient barcode and remove names and write them to "no_name_patient_id.txt, replace barcode with no name id and write it to data_mutations_extended.txt 
print("creating the data_mutations_extended file and the no_name_patient_id file....")                  
with open(file_name + ".txt", "r+") as file_case_list:
    firstline = file_case_list.readline()
    mutation_maf.write('\t'.join(first_line))
    line_contents = file_case_list.readline()   
    while line_contents!= "":
        more_lines = line_contents.split('\t')
        string_barCode = more_lines[n];
        UnderScore_list = string_barCode.split('_')
        str_list = UnderScore_list [0].split('-')
        if str_list[0] != "VALIDATION" and UnderScore_list[0] != "TRAIN":
            if str_list[2].find('NGSST') == -1:
                str_final = str_list[0]+'-' + str_list[1] + '-' + UnderScore_list[- 1] #T_M_B without name
                str_final_1 = str_list[0]+'-' + str_list[1] #Sample ID
                #print (str(type(collection_date_patientID[2])) + '\n')
                more_lines [n] = str_final
                no_name_list.write(str_final_1 + '\t' + more_lines[n] + '\t' + string_barCode +'\n')
                #+ get_disease(string) + '\t' + collection_date_patientID[1] + '\t' + collection_date_patientID[2])
                mutation_maf.write('\t'.join(more_lines))
        line_contents= file_case_list.readline()
#no_name_list.write('\n')

#create no_duplicate_id file 
print("creating the no_duplicate_id file....")     
no_name_list.seek(0)
line_contents = no_name_list.readline()
line_contents_previous = "xxx"
while line_contents != "":
        line_contents= line_contents.strip('\n')
        if line_contents != line_contents_previous:
            sample_id_list = line_contents.split('\t')
            disease = get_disease(sample_id_list[2]) #get patient disease
            collection_date_patientID = get_collection_date_patientID (sample_id_list[0]) #get collection date and EMPI
            collection_date_patientID = collection_date_patientID.split('\t')
            no_duplicate_list.write( line_contents + '\t' + disease + '\t' + collection_date_patientID[1] + '\t' + collection_date_patientID[2])
            # print(line_contents);
            line_contents_previous = line_contents;
        line_contents = no_name_list.readline()
            

#create the case_all.txt and case_sequenced.txt file
print("creating the case_all and case_sequenced files...")
no_duplicate_list.seek(0)
case_all = open(path_case_lists + '/' + "case_all.txt", "w+")
case_sequenced = open(path_case_lists + '/' + "case_sequenced.txt", "w+")
first_case_id = no_duplicate_list.readline().strip('\n')
id_list = first_case_id.split('\t')
case_all.write("cancer_study_identifier: " + file_name + '\n' + "stable_id: " + file_name + "_all" +'\n' 
+ "case_list_name: All Tumors" + '\n' + "case_list_description: All tumors" + '\n' + "case_list_ids: " + id_list[1])
case_sequenced.write("cancer_study_identifier: " + file_name + '\n' + "stable_id: " + file_name + "_sequenced" + '\n' + "case_list_name: Sequenced Tumors" + '\n'
+ "case_list_description: Sequenced tumors" + '\n' + "case_list_ids:  " + id_list[1])
line_contents = no_duplicate_list.readline()
while line_contents != "":
    line_contents = line_contents.strip('\n')
    id_list = line_contents.split('\t') 
    case_sequenced.write ('\t' + id_list[1])
    case_all.write ('\t' + id_list[1])
    line_contents = no_duplicate_list.readline()
    
#create the data_clinical_sample.txt and data_clinical_patient.txt file
print("creating the data_clinical sample file....")
no_duplicate_list.seek(0)

data_clinical_sample = open ("data_clinical_sample.txt", "w+")
data_clinical_sample.write("#Patient Identifier"+ '\t' + "Sample Identifier" + '\t' + "Cancer Type" + '\t' + "Collection Date" + '\n' +
"#Patient identifier" + '\t' + "Sample Identifier" + '\t' + "Cancer Type description" + '\t' + "Collection Date" + '\n' +
"#STRING" + '\t' + "STRING" + '\t' + "STRING" + '\t' + "STRING" + '\n' +
"#1" + '\t' + "1" + '\t' + "1" + '\t' + "1" + '\n' +
"PATIENT_ID" + '\t' + "SAMPLE_ID" + '\t' + "CANCER_TYPE" + '\t' + "COLLECTION_DATE")

#data_clinical_patient = open ("data_clinical_patient.txt", "w+")
#data_clinical_patient.write("#Patient Identifier"+ '\t' + "Patient Gender" + '\n' +
#"#Patient identifier" + '\t' + "Patient Gender" + '\n' +
#"#STRING" + '\t' "STRING" + '\n' +
#"#1" + '\t' + "1" + '\n' +
#"PATIENT_ID" + '\t' + "GENDER")


patient_id = 0 #patient id
line_contents = no_duplicate_list.readline()
while line_contents != "":
    line_contents = line_contents.strip('\n')
    id_disease_list = line_contents.split('\t')
    print((id_disease_list))
    patient_EMPI = id_disease_list[5]
    if patient_EMPI == '':
        patient_EMPI = id_disease_list[1]
    hashed_patient_EMPI = str(int(hashlib.sha256(patient_EMPI.encode('utf-8')).hexdigest(), 16) % 10**8)
    data_clinical_sample.write ( '\n' + hashed_patient_EMPI + '\t' + id_disease_list[1] + '\t' + id_disease_list[3] + '\t' + id_disease_list[4])
    
    ID_lookup_table.write(id_disease_list[0] + '\t' + id_disease_list[1] + '\n')
    #data_clinical_patient.write ( '\n' + patient_EMPI + '\t' + "Unknown")
    line_contents = no_duplicate_list.readline()

 
# make the meta files
print("creating the meta files...")
meta_study = open ("meta_study.txt", "w+")
meta_study.write ("type_of_cancer: " + "other" + '\n' + "cancer_study_identifier: " + file_name + '\n' +
                  "name: " + study_name + '\n' + "short_name: " + study_name_short + '\n' + "description: " + study_name_short +
                  '\n' + "citation: null" + '\n' + "groups: PUBLIC")
meta_clinical_sample = open ("meta_clinical_sample.txt", "w+")
meta_clinical_sample.write ("cancer_study_identifier: " + file_name + '\n' + "genetic_alteration_type: CLINICAL" +
                     '\n' + "datatype: SAMPLE_ATTRIBUTES" + '\n' + "data_filename: data_clinical_sample.txt")
#meta_clinical_patient = open ("meta_clinical_patient.txt", "w+")
#meta_clinical_patient.write ("cancer_study_identifier: " + file_name + '\n' + "genetic_alteration_type: CLINICAL" +
                    # '\n' + "datatype: PATIENT_ATTRIBUTES" + '\n' + "data_filename: data_clinical_patient.txt")
meta_mutations_extended = open ("meta_mutation_extended.txt", "w+")
meta_mutations_extended.write ("cancer_study_identifier: " + file_name + '\n' + "genetic_alteration_type: MUTATION_EXTENDED" +
                               '\n' + "datatype: MAF" + '\n' + "data_filename: data_mutations_extended.txt" + '\n' +
                               "stable_id: mutations" + '\n' + "show_profile_in_analysis_tab: true" + '\n' +
                               "profile_description: " + profile_description + '\n' +
                               "profile_name: Mutations")
#meta_cancer_type = open ("meta_cancer_type.txt", "w+")
#meta_cancer_type.write ("genetic_alteration_type: CANCER_TYPE" + '\n' + "datatype: CANCER_TYPE" + '\n' +
                       # "data_filename: cancer_type.txt")

# make the cancer_type file
#cancer_type = open ("cancer_type.txt", "w+")
#cancer_type.write(tumor_type + '\t' + "Adenocarcinoma,Melanoma" + '\t' + "lung,melanoma" +'\t' + "Black" + '\t' + "other" + '\n')


            
#close the files
print("closing the opened files...")
file_case_list.close()
no_name_list.close()
mutation_maf.close()
no_duplicate_list.close()
case_all.close()
case_sequenced.close()
data_clinical_sample.close()
#data_clinical_patient.close()
meta_study.close()
meta_clinical_sample.close()
#meta_clinical_patient.close()
meta_mutations_extended.close()
ID_lookup_table.close()
#meta_cancer_type.close()
#cancer_type.close()

#remove temp directory
print("removing the temp dir and files....")
#shutil.rmtree(parent_dir + '/' + "temp" + '/')

print("complete successfully.")




