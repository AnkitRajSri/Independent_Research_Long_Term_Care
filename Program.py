import numpy as np
import pandas as pd
import os
from datetime import datetime
from statsmodels.formula.api import ols

os.chdir(r'C:\Users\sriva\Desktop\Independent_Study')

#Importing data from csv
dataset = pd.read_csv('Jan2016-June2017Final Data Set-1.csv')
health_dataset = dataset.copy()

date = datetime.strptime(health_dataset.loc[0, 'AsOfDate'], "%m/%d/%Y")  

for i in range(health_dataset.shape[0]):
    health_dataset.loc[i, 'AsOfDate'] = datetime.strptime(health_dataset.loc[i, 'AsOfDate'], "%m/%d/%Y").strftime('%Y-%m-%d')
    
facilities = health_dataset['Facility'].drop_duplicates()

#Segragating the facilities having different EHR stage
ehrData0 = health_dataset[health_dataset['EHR'] == 0]
ehrData1 = health_dataset[health_dataset['EHR'] == 1]
ehrData2 = health_dataset[health_dataset['EHR'] == 2]

#Finding facilities with no stage change and the ones that changed their stages along with their date of transition
facilities_no_stage_change_0 = []
facilities_no_stage_change_1 = []
facilities_no_stage_change_2 = []
facilities_stage_changed_01 = []
facilities_stage_changed_02 = []
facilities_stage_changed_012 = []
facilities_stage_changed_12 = []
date_of_transition_01 = []
date_of_transition_02 = []
first_date_of_transition_012 = []
second_date_of_transition_012 = []
date_of_transition_12 = []

for i in facilities:
    if i in ehrData0['Facility'].values and i not in ehrData1['Facility'].values and i not in ehrData2['Facility'].values:
        facilities_no_stage_change_0.append(i)
    elif i not in ehrData0['Facility'].values and i in ehrData1['Facility'].values and i not in ehrData2['Facility'].values:
        facilities_no_stage_change_1.append(i) 
    elif i not in ehrData0['Facility'].values and i not in ehrData1['Facility'].values and i in ehrData2['Facility'].values:
        facilities_no_stage_change_2.append(i)
    elif i in ehrData0['Facility'].values and i in ehrData1['Facility'].values and i not in ehrData2['Facility'].values:
        facilities_stage_changed_01.append(i)
        date_of_transition = ehrData1.loc[ehrData1['Facility'] == i, 'AsOfDate'].min()
        date_of_transition_01.append(date_of_transition)
    elif i in ehrData0['Facility'].values and i not in ehrData1['Facility'].values and i in ehrData2['Facility'].values:
        facilities_stage_changed_02.append(i)
        date_of_transition = ehrData2.loc[ehrData2['Facility'] == i, 'AsOfDate'].min()
        date_of_transition_02.append(date_of_transition)
    elif i not in ehrData0['Facility'].values and i in ehrData1['Facility'].values and i in ehrData2['Facility'].values:
        facilities_stage_changed_12.append(i)
        date_of_transition = ehrData2.loc[ehrData2['Facility'] == i, 'AsOfDate'].min()
        date_of_transition_12.append(date_of_transition)
    else:
        facilities_stage_changed_012.append(i)
        date_of_transition1 = ehrData1.loc[ehrData1['Facility'] == i, 'AsOfDate'].min()
        first_date_of_transition_012.append(date_of_transition1)
        date_of_transition2 = ehrData2.loc[ehrData2['Facility'] == i, 'AsOfDate'].min()
        second_date_of_transition_012.append(date_of_transition2)

facilities_no_stage_change_0 = pd.DataFrame(facilities_no_stage_change_0)
facilities_no_stage_change_0.columns = ['Facility']


facilities_no_stage_change_1 = pd.DataFrame(facilities_no_stage_change_1)
facilities_no_stage_change_1.columns = ['Facility']

facilities_no_stage_change_2 = pd.DataFrame(facilities_no_stage_change_2)
facilities_no_stage_change_2.columns = ['Facility']

facility_tuple_01 = list(zip(facilities_stage_changed_01, date_of_transition_01))
facilities_stage_changed_01 = pd.DataFrame(facility_tuple_01, columns = ['Facility', 'DateOfTransition'])

facility_tuple_02 = list(zip(facilities_stage_changed_02, date_of_transition_02))
facilities_stage_changed_02 = pd.DataFrame(facility_tuple_02, columns = ['Facility', 'DateOfTransition'])

facility_tuple_012 = list(zip(facilities_stage_changed_012, first_date_of_transition_012, second_date_of_transition_012))
facilities_stage_changed_012 = pd.DataFrame(facility_tuple_012, columns = ['Facility', 'FirstDateOfTransition', 'SecondDateOfTransition'])

facility_tuple_12 = list(zip(facilities_stage_changed_12, date_of_transition_12))
facilities_stage_changed_12 = pd.DataFrame(facility_tuple_12, columns = ['Facility', 'DateOfTransition'])

#Creating new columns to store our dummy variables for event and group
health_dataset['posteventone'] = 0
health_dataset['posteventtwo'] = 0
health_dataset['groupOneA'] = 0
health_dataset['groupOneB'] = 0
health_dataset['groupOneC'] = 0
health_dataset['groupTwo'] = 0
health_dataset['groupThree'] = 0

#Populating the dummy values for each of the facilities
for f in facilities:
    if f in facilities_no_stage_change_0['Facility'].values:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupOneA'] = 1
    elif f in facilities_no_stage_change_1['Facility'].values:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupOneB'] = 1
    elif f in facilities_no_stage_change_2['Facility'].values:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupOneC'] = 1
    elif f in facilities_stage_changed_01['Facility'].values:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupTwo'] = 1
        date = facilities_stage_changed_01.loc[facilities_stage_changed_01['Facility'] == f, 'DateOfTransition'].values
        health_dataset.loc[(health_dataset['Facility'] == f) & (health_dataset['AsOfDate'].values >= date), 'posteventone'] = 1
    elif f in facilities_stage_changed_02['Facility'].values:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupThree'] = 1
        date = facilities_stage_changed_02.loc[facilities_stage_changed_02['Facility'] == f, 'DateOfTransition'].values
        health_dataset.loc[(health_dataset['Facility'] == f) & (health_dataset['AsOfDate'].values >= date), 'posteventtwo'] = 1
    elif f in facilities_stage_changed_12['Facility'].values:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupThree'] = 1
        date = facilities_stage_changed_12.loc[facilities_stage_changed_12['Facility'] == f, 'DateOfTransition'].values
        health_dataset.loc[(health_dataset['Facility'] == f) & (health_dataset['AsOfDate'].values >= date), 'posteventtwo'] = 1
    else:
        health_dataset.loc[health_dataset['Facility'] == f, 'groupTwo'] = 1
        health_dataset.loc[health_dataset['Facility'] == f, 'groupThree'] = 1
        date1 = facilities_stage_changed_012.loc[facilities_stage_changed_012['Facility'] == f, 'FirstDateOfTransition'].values
        date2 = facilities_stage_changed_012.loc[facilities_stage_changed_012['Facility'] == f, 'SecondDateOfTransition'].values
        health_dataset.loc[(health_dataset['Facility'] == f) & (health_dataset['AsOfDate'].values >= date1) & (health_dataset['AsOfDate'].values < date2), 'posteventone'] = 1
        health_dataset.loc[(health_dataset['Facility'] == f) & (health_dataset['AsOfDate'].values >= date2), 'posteventtwo'] = 1
        
#Exporting our master dataset to an excel
health_dataset.to_csv('Jan2016-June2017Final Data Set-1_Updated_MasterDataset_v2.csv')

#Segragating our master dataset for difference in differences regressions between groups
#Difference in differences for Group 1a vs Group 2
health_dataset_1a_vs_2 = health_dataset.drop(['groupOneB', 'groupOneC', 'groupThree', 'posteventtwo'], axis = 1)
health_dataset_1a_vs_2.to_csv('Jan2016-June2017Final Data Set-1_Updated_Dataset_1a_vs_2.csv')

#Assigning our independent variables for the regression
postevent_1a_vs_2 = health_dataset_1a_vs_2['posteventone'].values
treatgroup_1a_vs_2 = health_dataset_1a_vs_2['groupTwo'].values

#For clinical parameters
#Clinical Parameter 1: FiveStarAll
y_1a_vs_2_FiveStarAll = health_dataset_1a_vs_2['FiveStarAll'].values

reg_1a_vs_2_FiveStarAll = ols('y_1a_vs_2_FiveStarAll ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_FiveStarAll.summary()

#Clinical Parameter 2: FiveStarQuality
y_1a_vs_2_FiveStarQuality = health_dataset_1a_vs_2['FiveStarQuality'].values

reg_1a_vs_2_FiveStarQuality = ols('y_1a_vs_2_FiveStarQuality ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_FiveStarQuality.summary()

#Clinical Parameter 3: ComplaintTagPCT
y_1a_vs_2_ComplaintTagPCT = health_dataset_1a_vs_2['ComplaintTagPCT'].values

reg_1a_vs_2_ComplaintTagPCT = ols('y_1a_vs_2_ComplaintTagPCT ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_ComplaintTagPCT.summary()

#Clinical Parameter 4: FacilityDefIndex
y_1a_vs_2_FacilityDefIndex = health_dataset_1a_vs_2['FacilityDefIndex'].values

reg_1a_vs_2_FacilityDefIndex = ols('y_1a_vs_2_FacilityDefIndex ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_FacilityDefIndex.summary()

#Clinical Parameter 5: FailedRevtIndicator
y_1a_vs_2_FailedRevtIndicator = health_dataset_1a_vs_2['FailedRevtIndicator'].values

reg_1a_vs_2_FacilityDefIndex = ols('y_1a_vs_2_FailedRevtIndicator ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_FacilityDefIndex.summary()

#Clinical Parameter 6: RTHPCT
y_1a_vs_2_RTHPCT = health_dataset_1a_vs_2['RTHPCT'].values

reg_1a_vs_2_RTHPCT = ols('y_1a_vs_2_RTHPCT ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_RTHPCT.summary()

#For operational parameters
#Operational Parameter 1: StaffRetRate
y_1a_vs_2_StaffRetRate = health_dataset_1a_vs_2['StaffRetRate'].values

reg_1a_vs_2_StaffRetRate = ols('y_1a_vs_2_StaffRetRate ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_StaffRetRate.summary()

#Operational Parameter 2: PctOT
y_1a_vs_2_PctOT = health_dataset_1a_vs_2['PctOT'].values

reg_1a_vs_2_PctOT = ols('y_1a_vs_2_PctOT ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_PctOT.summary()

#Operational Parameter 3: TotTurnoverPct
y_1a_vs_2_TotTurnoverPct = health_dataset_1a_vs_2['TotTurnoverPct'].values

reg_1a_vs_2_TotTurnoverPct = ols('y_1a_vs_2_TotTurnoverPct ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_TotTurnoverPct.summary()

#Operational Parameter 4: Engaged
y_1a_vs_2_Engaged = health_dataset_1a_vs_2['Engaged'].values

reg_1a_vs_2_Engaged = ols('y_1a_vs_2_Engaged ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_Engaged.summary()

#For financial parameters
#Financial Parameter 1: ADCPct
y_1a_vs_2_ADCPct = health_dataset_1a_vs_2['ADCPct'].values

reg_1a_vs_2_ADCPct = ols('y_1a_vs_2_ADCPct ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_ADCPct.summary()

#Financial Parameter 2: BDebtPct
y_1a_vs_2_BDebtPct = health_dataset_1a_vs_2['BDebtPct'].values

reg_1a_vs_2_BDebtPct = ols('y_1a_vs_2_BDebtPct ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_BDebtPct.summary()

#Financial Parameter 3: SkilledPctMix
y_1a_vs_2_SkilledPctMix = health_dataset_1a_vs_2['SkilledPctMix'].values

reg_1a_vs_2_SkilledPctMix = ols('y_1a_vs_2_SkilledPctMix ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_SkilledPctMix.summary()

#Financial Parameter 4: PctBudget
y_1a_vs_2_PctBudget = health_dataset_1a_vs_2['PctBudget'].values

reg_1a_vs_2_PctBudget = ols('y_1a_vs_2_PctBudget ~ postevent_1a_vs_2 + treatgroup_1a_vs_2 + postevent_1a_vs_2*treatgroup_1a_vs_2', data = health_dataset_1a_vs_2).fit()
reg_1a_vs_2_PctBudget.summary()

#Difference in differences for Group 1a vs Group 3
health_dataset_1a_vs_3 = health_dataset.drop(['groupOneB', 'groupOneC', 'groupTwo', 'posteventone'], axis = 1)
health_dataset_1a_vs_3.to_csv('Jan2016-June2017Final Data Set-1_Updated_Dataset_1a_vs_3.csv')

#Assigning our independent variables for the regression
postevent_1a_vs_3 = health_dataset_1a_vs_3['posteventtwo'].values
treatgroup_1a_vs_3 = health_dataset_1a_vs_3['groupThree'].values

#For clinical parameters
#Clinical Parameter 1: FiveStarAll
y_1a_vs_3_FiveStarAll = health_dataset_1a_vs_3['FiveStarAll'].values

reg_1a_vs_3_FiveStarAll = ols('y_1a_vs_3_FiveStarAll ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_FiveStarAll.summary()

#Clinical Parameter 2: FiveStarQuality
y_1a_vs_3_FiveStarQuality = health_dataset_1a_vs_3['FiveStarQuality'].values

reg_1a_vs_3_FiveStarQuality = ols('y_1a_vs_3_FiveStarQuality ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_FiveStarQuality.summary()

#Clinical Parameter 3: ComplaintTagPCT
y_1a_vs_3_ComplaintTagPCT = health_dataset_1a_vs_2['ComplaintTagPCT'].values

reg_1a_vs_3_ComplaintTagPCT = ols('y_1a_vs_3_ComplaintTagPCT ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_ComplaintTagPCT.summary()

#Clinical Parameter 4: FacilityDefIndex
y_1a_vs_3_FacilityDefIndex = health_dataset_1a_vs_3['FacilityDefIndex'].values

reg_1a_vs_3_FacilityDefIndex = ols('y_1a_vs_3_FacilityDefIndex ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_2*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_FacilityDefIndex.summary()

#Clinical Parameter 5: FailedRevtIndicator
y_1a_vs_3_FailedRevtIndicator = health_dataset_1a_vs_3['FailedRevtIndicator'].values

reg_1a_vs_3_FacilityDefIndex = ols('y_1a_vs_3_FailedRevtIndicator ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_FacilityDefIndex.summary()

#Clinical Parameter 6: RTHPCT
y_1a_vs_3_RTHPCT = health_dataset_1a_vs_3['RTHPCT'].values

reg_1a_vs_3_RTHPCT = ols('y_1a_vs_3_RTHPCT ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_2', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_RTHPCT.summary()

#For operational parameters
#Operational Parameter 1: StaffRetRate
y_1a_vs_3_StaffRetRate = health_dataset_1a_vs_3['StaffRetRate'].values

reg_1a_vs_3_StaffRetRate = ols('y_1a_vs_3_StaffRetRate ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_StaffRetRate.summary()

#Operational Parameter 2: PctOT
y_1a_vs_3_PctOT = health_dataset_1a_vs_3['PctOT'].values

reg_1a_vs_3_PctOT = ols('y_1a_vs_3_PctOT ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_PctOT.summary()

#Operational Parameter 3: TotTurnoverPct
y_1a_vs_3_TotTurnoverPct = health_dataset_1a_vs_3['TotTurnoverPct'].values

reg_1a_vs_3_TotTurnoverPct = ols('y_1a_vs_3_TotTurnoverPct ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_TotTurnoverPct.summary()

#Operational Parameter 4: Engaged
y_1a_vs_3_Engaged = health_dataset_1a_vs_3['Engaged'].values

reg_1a_vs_3_Engaged = ols('y_1a_vs_3_Engaged ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_Engaged.summary()

#For financial parameters
#Financial Parameter 1: ADCPct
y_1a_vs_3_ADCPct = health_dataset_1a_vs_3['ADCPct'].values

reg_1a_vs_3_ADCPct = ols('y_1a_vs_3_ADCPct ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_ADCPct.summary()

#Financial Parameter 2: BDebtPct
y_1a_vs_3_BDebtPct = health_dataset_1a_vs_3['BDebtPct'].values

reg_1a_vs_3_BDebtPct = ols('y_1a_vs_3_BDebtPct ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_BDebtPct.summary()

#Financial Parameter 3: SkilledPctMix
y_1a_vs_3_SkilledPctMix = health_dataset_1a_vs_3['SkilledPctMix'].values

reg_1a_vs_3_SkilledPctMix = ols('y_1a_vs_3_SkilledPctMix ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_SkilledPctMix.summary()

#Financial Parameter 4: PctBudget
y_1a_vs_3_PctBudget = health_dataset_1a_vs_3['PctBudget'].values

reg_1a_vs_3_PctBudget = ols('y_1a_vs_3_PctBudget ~ postevent_1a_vs_3 + treatgroup_1a_vs_3 + postevent_1a_vs_3*treatgroup_1a_vs_3', data = health_dataset_1a_vs_3).fit()
reg_1a_vs_3_PctBudget.summary()

##Difference in differences for Group 2 vs Group 3
#health_dataset_2_vs_3 = health_dataset.drop(['groupOneB', 'groupOneB', 'groupOneC', 'posteventone'], axis = 1)
#health_dataset_2_vs_3.to_csv('Jan2016-June2017Final Data Set-1_Updated_Dataset_2_vs_3.csv')
#
##Assigning our independent variables for the regression
#postevent_2_vs_3 = health_dataset_2_vs_3['posteventtwo'].values
#treatgroup_2_vs_3 = health_dataset_2_vs_3['groupThree'].values
#
##For clinical parameters
##Clinical Parameter 1: FiveStarAll
#y_2_vs_3_FiveStarAll = health_dataset_2_vs_3['FiveStarAll'].values
#
#reg_2_vs_3_FiveStarAll = ols('y_2_vs_3_FiveStarAll ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_FiveStarAll.summary()
#
##Clinical Parameter 2: FiveStarQuality
#y_2_vs_3_FiveStarQuality = health_dataset_1a_vs_3['FiveStarQuality'].values
#
#reg_2_vs_3_FiveStarQuality = ols('y_2_vs_3_FiveStarQuality ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_FiveStarQuality.summary()
#
##Clinical Parameter 3: ComplaintTagPCT
#y_2_vs_3_ComplaintTagPCT = health_dataset_2_vs_3['ComplaintTagPCT'].values
#
#reg_2_vs_3_ComplaintTagPCT = ols('y_2_vs_3_ComplaintTagPCT ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_ComplaintTagPCT.summary()
#
##Clinical Parameter 4: FacilityDefIndex
#y_2_vs_3_FacilityDefIndex = health_dataset_2_vs_3['FacilityDefIndex'].values
#
#reg_2_vs_3_FacilityDefIndex = ols('y_2_vs_3_FacilityDefIndex ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_2*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_FacilityDefIndex.summary()
#
##Clinical Parameter 5: FailedRevtIndicator
#y_2_vs_3_FailedRevtIndicator = health_dataset_2_vs_3['FailedRevtIndicator'].values
#
#reg_2_vs_3_FacilityDefIndex = ols('y_2_vs_3_FailedRevtIndicator ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_FacilityDefIndex.summary()
#
##Clinical Parameter 6: RTHPCT
#y_2_vs_3_RTHPCT = health_dataset_1a_vs_3['RTHPCT'].values
#
#reg_2_vs_3_RTHPCT = ols('y_2_vs_3_RTHPCT ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_2', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_RTHPCT.summary()
#
##For operational parameters
##Operational Parameter 1: StaffRetRate
#y_2_vs_3_StaffRetRate = health_dataset_2_vs_3['StaffRetRate'].values
#
#reg_2_vs_3_StaffRetRate = ols('y_2_vs_3_StaffRetRate ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_StaffRetRate.summary()
#
##Operational Parameter 2: PctOT
#y_2_vs_3_PctOT = health_dataset_2_vs_3['PctOT'].values
#
#reg_2_vs_3_PctOT = ols('y_2_vs_3_PctOT ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_PctOT.summary()
#
##Operational Parameter 3: TotTurnoverPct
#y_2_vs_3_TotTurnoverPct = health_dataset_2_vs_3['TotTurnoverPct'].values
#
#reg_2_vs_3_TotTurnoverPct = ols('y_2_vs_3_TotTurnoverPct ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_TotTurnoverPct.summary()
#
##Operational Parameter 4: Engaged
#y_2_vs_3_Engaged = health_dataset_2_vs_3['Engaged'].values
#
#reg_2_vs_3_Engaged = ols('y_2_vs_3_Engaged ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_Engaged.summary()
#
##For financial parameters
##Financial Parameter 1: ADCPct
#y_2_vs_3_ADCPct = health_dataset_2_vs_3['ADCPct'].values
#
#reg_2_vs_3_ADCPct = ols('y_2_vs_3_ADCPct ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_ADCPct.summary()
#
##Financial Parameter 2: BDebtPct
#y_2_vs_3_BDebtPct = health_dataset_2_vs_3['BDebtPct'].values
#
#reg_2_vs_3_BDebtPct = ols('y_2_vs_3_BDebtPct ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_BDebtPct.summary()
#
##Financial Parameter 3: SkilledPctMix
#y_2_vs_3_SkilledPctMix = health_dataset_2_vs_3['SkilledPctMix'].values
#
#reg_2_vs_3_SkilledPctMix = ols('y_2_vs_3_SkilledPctMix ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_SkilledPctMix.summary()
#
##Financial Parameter 4: PctBudget
#y_2_vs_3_PctBudget = health_dataset_2_vs_3['PctBudget'].values
#
#reg_2_vs_3_PctBudget = ols('y_2_vs_3_PctBudget ~ postevent_2_vs_3 + treatgroup_2_vs_3 + postevent_2_vs_3*treatgroup_2_vs_3', data = health_dataset_2_vs_3).fit()
#reg_2_vs_3_PctBudget.summary()