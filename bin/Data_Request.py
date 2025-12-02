#!/usr/bin/env python3

from typing import Tuple, List
import sys
import re
import argparse
import requests
import json
import numpy as np
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class AppError(Exception):
    def __init__(self, error: str = ""):
        self.error = error

    def __str__(self):
        return self.error

def parse_var(s) -> Tuple[str, str]:
    try:
        key, value = s.split("=")
        return (key, value)
    except ValueError:
        raise AppError(f"Cannot parse {s} parameter. Missing '='. Required format : 'item=value'")

def parse_vars(items):
    """
    Parse a series of key-value pairs and return a dictionary
    """
    # Empty element
    if not items:
        return {}
    d = {}

    for item in items:
        key, value = parse_var(item)
        d[key] = value
    return d

def parse_auth(auth_string: str) -> tuple:
    """Parse and format the authentication given in CLI parameters

    :param auth_string: str: The string given in input of the CLI.
    :return tuple: (user, password)
    :raise AppError: if the format of the auth_string is not correct
    """
    try:
        user, password = auth_string.split(":")
    except ValueError:
        raise AppError("Cannot parse authentification parameter. Use 'user:password' format")
    if not user or not password:
        raise AppError("Empty user or password authentication. Use '--auth user:password'")
    return (user, password)

def fetch_xapi_data(headers: dict, params: dict, auth: tuple, url: str, port: int):
    """Generator which get xAPI data on the LRS.

    Yield dictionnary of data instead of pulling the whole xapi dataset into a list
    Avoid saturating memory (for a 500k statements dataset, decrease memory consumption from 1GB to 120MB)
    """
    if not url.startswith("http"):
        url = f"http://{url}"
    response = requests.get(url=f"{url}:{port}/trax/ws/xapi/statements", auth=auth, headers=headers, params=params)
    if response.status_code != 200:
        raise AppError(f"Request '{response.request.url}' response: {response.status_code}. Reason: {response.text} ")
    data = response.json()
    if not data:
        raise AppError(f"Request '{response.request.url}' no json data. Reason: {response.text} ")
    yield data["statements"]
    while data.get("more"):
        response = requests.get(url=data["more"], auth=auth, headers=headers, params=params)
        data = response.json()
        yield data["statements"]
        
def fetch_agent_profiles_data(headers: dict, auth: tuple, url: str, port: int, listAgents):
    """Generator which get agent profiles on the LRS, where the demographic data is stored

    Yield dictionnary of data instead of pulling the whole profiles dataset into a list
    Avoid saturating memory (for a 500k statements dataset, decrease memory consumption from 1GB to 120MB)
    """
    if not url.startswith("http"):
        url = f"http://{url}"
    for agent in listAgents:
        match = re.search(r"mailto:(\d+)", str(agent))
        if match:
            profileId = match.group(1)
        params={"agent":json.dumps(agent),"profileId":profileId}
        response = requests.get(url=f"{url}:{port}/trax/ws/xapi/agents/profile", auth=auth, headers=headers, params=params)
        if response.status_code != 200:
            raise AppError(f"Request '{response.request.url}' response: {response.status_code}. Reason: {response.text} ")
        data = response.json()
        yield data
        
def fetch_activity_profiles_data(headers: dict, auth: tuple, url: str, port: int, listActivities): 
    """Generator which get activity profiles on the LRS, where inforamtion about the course and exam deadlines are stored

    Yield dictionnary of data instead of pulling the whole profiles dataset into a list
    Avoid saturating memory (for a 500k statements dataset, decrease memory consumption from 1GB to 120MB)
    """
    if not url.startswith("http"):
        url = f"http://{url}"
    for activity in listActivities:
        match = re.search(r"_([0-9]+)$", str(activity))
        if match:
            profileId = match.group(1) 
        params={"activityId":activity,"profileId":profileId}
        response = requests.get(url=f"{url}:{port}/trax/ws/xapi/activities/profile", auth=auth, headers=headers, params=params)
        if response.status_code != 200:
            raise AppError(f"Request '{response.request.url}' response: {response.status_code}. Reason: {response.text} ")
        data = response.json()
        yield data   
        

def parse_aactivity_profile_data(data_generator_profile):
    """Extract data from xapi activity profiles.
    Get demographic information as well as class labels 
    :return: -> course_data : dataframe with  columns 
    """
    all_data_profiles: List[Tuple[str, str, str,str,str,str,str,str,str,str,str,str,str,str,str,str]] = []
    {'Exams': [{'id': '1', 'Deadline': '29/09/2017'}, 
               {'id': '3', 'Deadline': '23/11/2017'}, {'id': '5', 'Deadline': '23/01/2018'}, 
               {'id': '7', 'Deadline': '20/03/2018'}, {'id': '9', 'Deadline': '19/05/2018'}, 
               {'id': '11', 'Deadline': '20/06/2018'}], 
     'EndDate': '31/07/2018', 'StartDate': '01/09/2017', 'course_id': '1562'}
    for profile in data_generator_profile:
        profile_fields=(profile['course_id'],
                        profile['StartDate'],
                        profile['EndDate'],
                        profile['Exams'][0]['id'],
                        profile['Exams'][0]['Deadline'],
                        profile['Exams'][1]['id'],
                        profile['Exams'][1]['Deadline'],
                        profile['Exams'][2]['id'],
                        profile['Exams'][2]['Deadline'],
                        profile['Exams'][3]['id'],
                        profile['Exams'][3]['Deadline'],
                        profile['Exams'][4]['id'],
                        profile['Exams'][4]['Deadline'],
                        profile['Exams'][5]['id'],
                        profile['Exams'][5]['Deadline'])
        
        all_data_profiles.append(profile_fields)
    course_data = pd.DataFrame(all_data_profiles, columns=["course_ID", "StartDate","EndDate","ID_Exam_1", "Deadline_1",
                                                          "ID_Exam_2", "Deadline_2","ID_Exam_3", "Deadline_3",
                                                          "ID_Exam_4", "Deadline_4","ID_Exam_5", "Deadline_5",
                                                          "ID_Exam_6", "Deadline_6"])
    return course_data


    
def parse_agent_profile_data(data_generator_profile):
    """Extract data from xapi agent profiles.

    Get demographic information as well as class labels 

    :return: -> demographic_data : dataframe with 8 columns ("student_ID", "sex","enrollmentDate","startDate", "scholarship",
                                                            "repeatingClass","AvgScore","classLabel")
    """
    all_data_profiles: List[Tuple[str, str, str,str,str,str,int,int]] = []
    for profile in data_generator_profile:
        profile_fields=(profile['userid'],
                        profile['Sex'],
                        profile['RegistrationDate'],
                        profile['StartDate'],
                        profile['scholarship'],
                        profile['repeatingClass'],
                        profile['AvgScore'],
                        profile['classLabel']
                        )
        all_data_profiles.append(profile_fields) 
    demographic_data = pd.DataFrame(all_data_profiles, columns=["student_ID", "sex","enrollmentDate","startDate", "scholarship",
                                                          "repeatingClass","AvgScore","classLabel"])
    return demographic_data
        
        
       
def parse_data(data_generator):
    """Extract data from the genrator xapi statements.

    According to the verb type : it Gets actor, object , verb, context, result 

    :return: -> 2 dataframes : data_log contains the logs from viewed and submitted ("student_ID", "object_ID","course_ID","timestamp", "action")
                               data_score contains the scores from scored ("student_ID", "object_ID","course_ID","grade","timestamp", "action","agentProfile")
    """
    all_data_log: List[Tuple[str, str, str,str,str]] = []
    all_data_score: List[Tuple[str, str, str,int,str,str,str]] = []
    for xapi_data in data_generator:
        data_scored = []
        data_log= []
        for statement in xapi_data:
            match = re.search(r"mailto:(\d+)", statement["actor"]["mbox"])
            if match:
                studentid = match.group(1)
            
        
            if (statement["verb"]["id"]=="http://adlnet.gov/expapi/verbs/scored"):
                statement_fields= (studentid,
                                statement["object"]["id"],
                                statement["context"]["contextActivities"]["parent"][0]["id"],
                                statement["result"]["score"]["raw"],
                                statement["timestamp"],
                                statement["verb"]["id"],
                                statement["actor"])
                data_scored.append(statement_fields)
                
            elif(statement["verb"]["id"]=="http://activitystrea.ms/schema/1.0/submit"):
                statement_fields = (studentid,
                                    statement["object"]["id"],
                                    statement["context"]["contextActivities"]["parent"][0]["id"],
                                    statement["timestamp"],
                                    statement["verb"]["id"])
                data_log.append(statement_fields)
            
            #viewed processing   
            else:
                if "context" in statement:
                    #context exists
                    statement_fields=(studentid,
                                    statement["object"]["id"],
                                    statement["context"]["contextActivities"]["parent"][0]["id"],
                                    statement["timestamp"],
                                    statement["verb"]["id"]
                                    )
                    
                    
                else: 
                    #context does not exist
                    statement_fields=(studentid,
                                    statement["object"]["id"],
                                    statement["object"]["id"],
                                    statement["timestamp"],
                                    statement["verb"]["id"])
                data_log.append(statement_fields)
        all_data_log.extend(data_log)
        all_data_score.extend(data_scored)
    data_log = pd.DataFrame(all_data_log, columns=["student_ID", "object_ID","course_ID","timestamp", "action"])
    data_score = pd.DataFrame(all_data_score, columns=["student_ID", "object_ID","course_ID","grade","timestamp", "action","agentProfile"])
            
    return data_log, data_score
            
                        
def process_data(data_log,data_score,demographic_data,course_data):
    """Process the data and prepare the features.
    :param data: data_log: pandas.Dataframe, data_score: pandas.Dataframe,demographic_data :pandas.Dataframe, course_data=pandas.Dataframe
    :return: pandas.DataFrame: the pandas dataframe normalized to be used for training with the computed features and the class label
    """
    #merge data-log and demographic_data
    data_log_demographic= pd.merge(data_log,demographic_data,on='student_ID', how='inner')
    # Convert 'timestamp' to datetime
    data_log_demographic['newtimestamp'] = pd.to_datetime(data_log_demographic.timestamp,utc=True)
    data_log_demographic['actual_week']=data_log_demographic['newtimestamp'].dt.isocalendar().week
    data_log_demographic['computed_week']= np.where(data_log_demographic['actual_week'] >=35,
                                                    data_log_demographic['actual_week']-34,data_log_demographic['actual_week']+18)
    #convert 'startDate' to datetime 
    data_log_demographic['newStartDate'] = pd.to_datetime(data_log_demographic.startDate,dayfirst=True)
    data_log_demographic['actual_start_week']=data_log_demographic['newStartDate'].dt.isocalendar().week
    data_log_demographic['computed_start_week']= np.where(data_log_demographic['actual_start_week'] >=35,
                                                    data_log_demographic['actual_start_week']-34,data_log_demographic['actual_start_week']+18)
    
    
    # compute the number of log per week per student 
    list_computed_week=sorted(data_log_demographic["computed_week"].unique())
    Final_feature_data=pd.DataFrame(columns=["student_ID","sex","enrollmentDate",
                                             "startDate", "scholarship","repeatingClass",
                                             "AvgScore","classLabel","log_week","computed_week"])
    for week in list_computed_week:
        #DataFrame that contains the logs of the students who started before or during the current week
        df_logs_till_week=data_log_demographic.loc[data_log_demographic['computed_start_week'] <=week]
        df_logs_current_week=data_log_demographic.loc[data_log_demographic['computed_week'] == week]
        df_computed_features= df_logs_till_week.drop_duplicates(subset='student_ID')[["student_ID","sex","enrollmentDate","startDate", "scholarship",
                                                                                      "repeatingClass","AvgScore","classLabel"]]
        # Determine frequency of student IDs in df_logs_current_week
        log_week_dict = df_logs_current_week['student_ID'].value_counts().to_dict()  
        # Add frequency as a new column in df1 and fill missing values with 0
        df_computed_features['log_week'] = df_computed_features['student_ID'].map(log_week_dict).fillna(0).astype(int)
        df_computed_features['computed_week']=week
        Final_feature_data=pd.concat([Final_feature_data,df_computed_features])
        
    # Add the feature cumulative_logs per student till a gicen week 
    feature_data=pd.DataFrame(columns=["classLabel","computed_week","student_ID",
                                       "sex", "scholarship","repeatingClass",
                                       "log_week","cumulative_logs"])
    for week in list_computed_week:
        # Filter the DataFrame for weeks up to the given week
        filtered_df = Final_feature_data[Final_feature_data['computed_week'] <= week].copy()
        # Calculate the cumulative logs per student
        # Convert 'total_logs' column to numeric data type
        filtered_df['log_week'] = pd.to_numeric(filtered_df['log_week'])
        filtered_df.loc[:,'cumulative_logs'] = filtered_df.groupby('student_ID')['log_week'].cumsum()
        feature_data=pd.concat([feature_data,filtered_df])  
    
    for week in list_computed_week:
        cols=["classLabel","sex", "scholarship","repeatingClass","log_week","cumulative_logs"]
        data=feature_data[feature_data['computed_week'] == week]
        data[cols].to_csv(f"logSP31_w{week}.csv",index=False)
        

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(
        description="Request GET to Trax LRS and extract required features from the database"
    )
    argument_parser.add_argument(
        "--headers",
        metavar="KEY=VALUE",
        nargs="+",
        default="X-Experience-API-Version=1.0.3",
        help="headers of the GET request",
    )
    argument_parser.add_argument("-o", "--output",help=" Filename for training data")
    argument_parser.add_argument("-p", "--parameters", metavar="KEY=VALUE", nargs="+", help="Parameters of the requets")
    # Define default as testsuite:password because it's the default for TRAX LRS
    # It's not a good practice to define static value in a script but this program
    # will mainly serve on the LOLA platform
    argument_parser.add_argument(
        "-a",
        "--auth",
        metavar="user:password",
        type=str,
        default="testsuite:password",
        help="Basic Authentication colon separated",
    )
    argument_parser.add_argument("--url", type=str, help="TRAX LRS url", required=True)
    argument_parser.add_argument("--port", type=str, help="TRAX LRS port", required=True)
   
    if len(sys.argv) == 1:
        argument_parser.print_help()
        sys.exit()
    args = argument_parser.parse_args()
    # retrieve xAPI data
    data_generator_xAPI = fetch_xapi_data(headers=parse_vars(args.headers),
                                          params=parse_vars(args.parameters),
                                          auth=parse_auth(args.auth),
                                          url=args.url,
                                          port=args.port
                                          )
    # Parse the xAPI data : output 2 pandas.Dataframe , one for the logs (viewed and submit) and the second for the grades (scored)
    # in the data_scores, we recuperate all the data about the actor in the column "agentProfile", this information is used to recuperate
    # agent profiles
    data_log, data_scores= parse_data(data_generator_xAPI)
   # Retrieve Agent Profile to get demographic data and the the class label
    #1 get the list of actors : required for the request to get the agent profiles (demographic data)
    unique_values_agents = data_scores.drop_duplicates(subset='student_ID')
    list_agent=unique_values_agents['agentProfile']
    data_gearator_Ag_Profile=fetch_agent_profiles_data(headers=parse_vars(args.headers),
                                                       auth=parse_auth(args.auth),
                                                       url=args.url,
                                                       port=args.port,
                                                       listAgents=list_agent
                                                       )
    # Parse the agent profile data : output 1 pandas.Dataframe with demographic data abiut the students
    data_demographic = parse_agent_profile_data(data_gearator_Ag_Profile)
    # Retrieve Activity Profile to get information about the courses 
    list_activity=data_scores['course_ID'].unique()
    data_generator_Ac_Profile= fetch_activity_profiles_data(headers=parse_vars(args.headers),
                                                            auth=parse_auth(args.auth),
                                                            url=args.url,
                                                            port=args.port,
                                                            listActivities=list_activity)
    course_data=parse_aactivity_profile_data(data_generator_Ac_Profile)
    final_data=process_data(data_log=data_log, 
                            data_score=data_scores,
                            demographic_data=data_demographic,
                            course_data=course_data)
