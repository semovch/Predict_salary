import os

import requests
import datetime

from terminaltables import AsciiTable
from dotenv import load_dotenv


def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)/2
    elif salary_from:
        return salary_from * 1.2
    else:
        return salary_to * 0.8


def make_table(title, vacancies_stat):
    table_data = [
        ['Язык программирования', 'Предполагаемая зарплата', 'Вакансий найдено', 'Вакансий обработано']
    ]
    for lang in vacancies_stat:
        table_data.append([lang, (vacancies_stat[lang]['average_salary']),
                           (vacancies_stat[lang]['vacancies_found']), (vacancies_stat[lang]['vacancies_processed'])])
    table_instance=AsciiTable(table_data, title)
    return(table_instance.table)


def predict_rub_salary_sj(url, languages, sj_secret_key, sj_msc_index,  sj_max_numb_page):
    vacancies_stat = {}
    for language in languages:
        page=0
        all_salaries=[]
        while page <  sj_max_numb_page:
            parameters={
                'keywords': ['программист', f'{language}'],
                'town': sj_msc_index,
                'page': page
                    }
            headers={
                'X-Api-App-Id': sj_secret_key

                    }
            page_response=requests.get(url, headers=headers, params=parameters)
            page_response.raise_for_status()
            page_vacancies = page_response.json() 
            for vacancy in page_vacancies['objects']:
                if vacancy['currency'] == 'rub' and vacancy['payment_from'] or vacancy['payment_to']:
                        all_salaries.append(predict_rub_salary(vacancy['payment_from'], vacancy['payment_to']))
                else:
                    pass
            if len(all_salaries) != 0:    
                vacancies_stat[f'{language}'] = dict([('average_salary', int(sum(all_salaries)/len(all_salaries))),
                                                            ('vacancies_found', page_vacancies['total']), ('vacancies_processed', len(all_salaries))])
            else:
                pass
            page += 1
    return vacancies_stat
    


def predict_rub_salary_hh_Moscow(languages, date_month_ago, url, hh_msc_index):
    vacancies_stat = {}    
    for language in languages:
        page=0
        pages_number=1
        all_salaries=[]
        while page < pages_number:
            parameters={
                'text': f'программист {language}',
                'area': hh_msc_index,
                'date_from': date_month_ago,
                'page': page
                    }
            page_response=requests.get(url, params=parameters)
            page_response.raise_for_status()
            page_vacancies = page_response.json()
            for vacancy in (page_vacancies['items']):
                if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
                    all_salaries.append(predict_rub_salary(vacancy['salary']['from'],
                                        vacancy['salary']['to']))
                else:
                    pass
            if len(all_salaries) != 0:
                vacancies_stat[f'{language}'] = dict([('average_salary', int(sum(all_salaries)/len(all_salaries))),
                                                            ('vacancies_found', page_vacancies['found']), ('vacancies_processed', len(all_salaries))])
            else: 
                pass
            pages_number=page_response.json()['pages']
            page += 1
    return vacancies_stat
    


def main():
    load_dotenv('.env')
    sj_secret_key=os.environ['SUPER_JOB_SECRET_KEY']
    languages=['Python', 'Javascript', 'Scala', 'Shell', 'Go', 'C#', 'C++', 'Java', 'Ruby']
    hh_url='https://api.hh.ru/vacancies'
    sj_url='https://api.superjob.ru/2.0/vacancies/'
    hh_msc_index = 1
    sj_msc_index = 4
    sj_max_numb_page = 25
    sj_title = 'SuperJob_Moscow'
    hh_title = 'HeadHunter_Moscow'
    date_month_ago = datetime.date.today() - datetime.timedelta(days=30)
    print(make_table(hh_title, predict_rub_salary_hh_Moscow(languages, date_month_ago, hh_url, hh_msc_index)), make_table(sj_title, predict_rub_salary_sj(sj_url, languages, sj_secret_key, sj_msc_index,  sj_max_numb_page)))
    
    
if __name__ == '__main__':
    main()

