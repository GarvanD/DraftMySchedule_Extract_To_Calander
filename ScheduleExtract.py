# Author: Garvan Doyle
# Email: garvandoyle@gmail.com
# Date: 12/09/2019

import arrow
from ics import Calendar, Event
import mechanicalsoup
from bs4 import BeautifulSoup
import pprint
import re
import getpass
import recurring_ical_events

class Schedule:
    def dayOfWeek(self,day,semester):
        date = '08'
        if semester == 1:
            if day == "Mon":
                date = '09'
            if day == "Tues":
                date = '10'
            if day == "Wed":
                date = '11'
            if day == "Thurs":
                date = '12'
            if day == "Fri":
                date = '13' 
        else:
            if day == "Mon":
                date = '06'
            if day == "Tues":
                date = '07'
            if day == "Wed":
                date = '08'
            if day == "Thurs":
                date = '09'
            if day == "Fri":
                date = '10' 

        return date

    def ClassInSchedule(self,day,start_time,end_time,course_code,class_type,location,instructor,section,semester,w):
        e = Event()
        if semester == 1:
            timeframe = '2019-09-'+ self.dayOfWeek(day,1)
        elif semester == 2:
            timeframe = '2020-01-'+ self.dayOfWeek(day,2)   
        e = Event()
        e.name = course_code + ' ' + class_type + ' ' + section
        if semester == 1:
            e.begin = arrow.get(timeframe + ' ' + start_time.strip(),'YYYY-MM-DD HH:mm A').shift(hours=4,weeks=w)
            e.end = arrow.get(timeframe + ' '+ end_time.strip(),'YYYY-MM-DD HH:mm A').shift(hours=4,weeks=w)
        else:
            e.begin = arrow.get(timeframe + ' ' + start_time.strip(),'YYYY-MM-DD HH:mm A').shift(hours=5,weeks=w)
            e.end = arrow.get(timeframe + ' '+ end_time.strip(),'YYYY-MM-DD HH:mm A').shift(hours=5,weeks=w)

        e.location = location
        return e



    def getClassList(self,username,password):
        browser = mechanicalsoup.StatefulBrowser()
        browser.open("https://draftmyschedule.uwo.ca/login.cfm")

        browser.select_form('#loginForm')
        browser["txtUsername"] = username
        browser["txtPassword"] = password
        response = browser.submit_selected()
        browser.select_form('form')
        response = browser.submit_selected()

        browser.open("https://draftmyschedule.uwo.ca/secure/current_timetable.cfm")
        html_file = browser.get_current_page()

        data = []
        table = html_file.find_all('div', attrs={'class': re.compile('^class_box.*')})
        class_name = html_file.find_all('span', attrs={'class': re.compile("h_class_text")})

        for index in range(len(table)):
            item = str(table[index]).split('&')
            class_info = []
            for index, x in enumerate(item):
                if 'pull-right' in x: 
                    class_info.append(item[index+1].split(';')[1].split('&')[0])   
            if len(class_info) > 0:
                data.append(class_info)

        for index,i in enumerate(class_name):
            data[index].append(i.text)
        return data

    def __init__(self):
        cal = Calendar()
        class_list = None
        try:
            u = input("Username: ")
            p = getpass.getpass() 
            class_list = self.getClassList(u,p)
        except Exception as error: 
            print('ERROR', error) 
        previous_day = None
        semester = 1
        for c in class_list:
            for week in range(13):
                if previous_day == "Fri" and c[4] == "Mon":
                    semester = 2
                previous_day = c[4]
                cal.events.add(self.ClassInSchedule(c[4], c[3].split('-')[0],c[3].split('-')[1],c[6],c[0],c[5],c[2],c[1],semester,week))
        with open('Class Schedule.ics', 'w+') as my_file:
            my_file.writelines(cal)
            my_file.close()

if __name__ == '__main__':
    s = Schedule()