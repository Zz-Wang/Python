#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      ewazhiz
#
# Created:     05-05-2015
# Copyright:   (c) ewazhiz 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import random

#define a class called 'Customer'
class Customer:
    def __init__(self,arrival_date,service_start_date,service_time):
        self.arrival_date=arrival_date
        self.service_start_date=service_start_date
        self.service_time=service_time
        self.service_end_date=self.service_start_date+self.service_time
        self.wait=self.service_start_date-self.arrival_date

#a simple function to sample from negative exponential
def neg_exp(lambd):
    return random.expovariate(lambd)
def QSim(lambd=False,mu=False,simulation_time=False):
    """
    This is the main function to call to simulate an MM1 queue.
    """
    #If parameters are not input prompt
    if not lambd:
        lambd=input('Inter arrival rate: ')
    if not mu:
            mu=input('Service rate: ')
    if not simulation_time:
            simulation_time=input('Total simulation time: ')
    #Initialise clock
    t=0
    #Initialise empty list to hold all data
    Customers=[]
#----------------------------------
#The actual simulation happens here:
    while t<simulation_time:
        #calculate arrival date and service time for new customer
        if len(Customers)==0:
            arrival_date=neg_exp(lambd)
            service_start_date=arrival_date
        else:
            arrival_date+=neg_exp(lambd)
            service_start_date=max(arrival_date,Customers[-1].service_end_date)
        service_time=neg_exp(mu)
        #create new customer
        Customers.append(Customer(arrival_date,service_start_date,service_time))
        #increment clock till next end of service
        t=arrival_date
    #----------------------------------
    #calculate summary statistics
    Waits=[a.wait for a in Customers]
    Mean_Wait=sum(Waits)/len(Waits)

    Total_Times=[a.wait+a.service_time for a in Customers]
    Mean_Time=sum(Total_Times)/len(Total_Times)

    Service_Times=[a.service_time for a in Customers]
    Mean_Service_Time=sum(Service_Times)/len(Service_Times)

    Utilisation=sum(Service_Times)/t

    #output summary statistics to screen
    print ""
    print "Summary results:"
    print ""
    print "Number of customers: ",len(Customers)
    print "Mean Service Time: ",Mean_Service_Time
    print "Mean Wait: ",Mean_Wait
    print "Mean Time in System: ",Mean_Time
    print "Utilisation: ",Utilisation
    print ""

    return


