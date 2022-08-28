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


def table(title, dictionary):
    table_data = [
        ['Язык программирования', 'Предполагаемая зарплата', 'Вакансий найдено', 'Вакансий обработано']
    ]
    for lang in dictionary:
        table_data.append([lang, str(dictionary[lang]['average_salary']),str(dictionary[lang]['vacancies_found']), str(dictionary[lang]['vacancies_processed'])])
    table_instance=AsciiTable(table_data, title)
    return(table_instance.table)


def predict_rub_salary_sj(url, languages, secret_key_sj):
    list_for_dict=[]
    for language in languages:
        page=0
        all_salaries=[]
        while page < 25:
            parameters={
                'keywords': ['программист', f'{language}'],
                'town': 4,
                'page': page
                    }
            headers={
                'X-Api-App-Id': secret_key_sj

                    }
            page_response=requests.get(url, headers=headers, params=parameters)
            page_response.raise_for_status()
            for vacancy in page_response.json()['objects']:
                if vacancy['currency'] == 'rub':
                    if vacancy['payment_from'] or vacancy['payment_to']:
                        all_salaries.append(predict_rub_salary(vacancy['payment_from'], vacancy['payment_to']))
                    else:
                        pass
                else:
                    pass
            language_stat=f'{language}', dict([('average_salary', int(sum(all_salaries)/len(all_salaries))),
                            ('vacancies_found', page_response.json()['total']), ('vacancies_processed', len(all_salaries))])
            list_for_dict.append(language_stat)
            page += 1
    vacancies_dict=dict(list_for_dict)
    title='Super_Job_Moscow'
    return(table(title, vacancies_dict))


def predict_rub_salary_hh_Moscow(languages, date_month_ago, url):
    list_for_dict=[]
    for language in languages:
        page=0
        pages_number=1
        all_salaries=[]
        while page < pages_number:
            parameters={
                'text': f'программист {language}',
                'area': '1',
                'date_from': date_month_ago,
                'page': page
                    }
            page_response=requests.get(url, params=parameters)
            page_response.raise_for_status()
            for item in (page_response.json()['items']):
                if item['salary']:
                    if item['salary']['currency'] == 'RUR':
                        all_salaries.append(predict_rub_salary(item['salary']['from'],
                                            item['salary']['to']))
                    else:
                        pass
                else:
                    pass
            language_stat=f'{language}', dict([('average_salary', int(sum(all_salaries)/len(all_salaries))),
                ('vacancies_found', page_response.json()['found']), ('vacancies_processed', len(all_salaries))])
            list_for_dict.append(language_stat)
            vacancies_dict=dict(list_for_dict)
            pages_number=page_response.json()['pages']
            page += 1
    title='HeadHunter_Moscow'
    vacancies_dict=vacancies_dict
    return(table(title, vacancies_dict))


def main():
    load_dotenv('.env')
    secret_key_sj=os.environ['SECRET_KEY_SUPER_JOB']
    languages=['Python', 'Javascript', 'Scala', 'Shell', 'Go', 'C#', 'C++', 'Java', 'Ruby']
    url_hh='https://api.hh.ru/vacancies'
    url_sj='https://api.superjob.ru/2.0/vacancies/'
    date_month_ago=datetime.date.today() - datetime.timedelta(days=30)
    print(predict_rub_salary_hh_Moscow(languages, date_month_ago, url_hh),
        predict_rub_salary_sj(url_sj, languages, secret_key_sj))


if __name__ == '__main__':
    main()
