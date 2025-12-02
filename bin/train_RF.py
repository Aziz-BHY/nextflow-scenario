#!/usr/bin/env python3
from sklearn.ensemble import RandomForestClassifier
import pickle
import argparse
import pandas as pd 
import sys
from sklearn.model_selection import train_test_split


#def train_RF(alg_params, train_data,trained_model_name):
	
	#Create model instance using Sickit learn library
#	model_RF = RandomForestClassifier(n_estimators=int(alg_params[0]), criterion=str(alg_params[1]), random_state=int(alg_params[2]))


#	df_train=pd.read_csv(train_data)

#	X_train=df_train.iloc[:, 1:].values
#	y_train=df_train.iloc[:,0].values

#	model_RF.fit(X_train, y_train)
#	pickle.dump(model_RF, open(trained_model_name, 'wb'))



#create a model for each learning week
def train_RF(alg_params, train_data,trained_model_name):
	
	#Create model instance using Sickit learn library
	model_RF = RandomForestClassifier(n_estimators=int(alg_params[0]), criterion=str(alg_params[1]), random_state=int(alg_params[2]))


	df_train=pd.read_csv(train_data)

	X_train=df_train.iloc[:, 1:].values
	y_train=df_train.iloc[:,0].values

	model_RF.fit(X_train, y_train)
	pickle.dump(model_RF, open(trained_model_name, 'wb'))



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Train the RF model')
	parser.add_argument("--p", action='store', dest='listparamsAlg',type=str, nargs='*', default=[],help="List params of the algorithm")
	parser.add_argument("--a",type=str,help=" The Path to trainset file")
	parser.add_argument("--m", type=str, help="The filename to save the trained model")
	if len(sys.argv)==1:
		parser.print_help()
		sys.exit()
	args = parser.parse_args()
	print(args.listparamsAlg)

	train_RF(alg_params=args.listparamsAlg,
		train_data=args.a,
		trained_model_name=args.m
		)
