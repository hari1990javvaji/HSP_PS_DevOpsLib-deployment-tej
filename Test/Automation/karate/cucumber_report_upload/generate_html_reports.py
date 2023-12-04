import sys
import os
import traceback
from jsonHTML import htmlConvertion
html_convert = htmlConvertion()


def html_report(reg_json_file_path, non_reg_json_file_path, project_execution_summary_json, html_report_location):
    """

    :param reg_json_file_path: Regression json file
    :param non_reg_json_file_path: Non Regression json file
    :param project_execution_summary_json: Summary Report of test execution json file
    :param html_report_location: Location where Regression and non regression HTML files will be stored.
    :return: HTML Files will be generated. Nothing will be returned from this utility
    """

    try:
        if os.path.exists(reg_json_file_path):
            html_convert.htmlFileConvertion(reg_json_file_path,
                                            project_execution_summary_json,
                                            'html_structure.html',
                                            html_report_location + '/Regression_TestCase_Report.html')

        if os.path.exists(non_reg_json_file_path):
            html_convert.htmlFileConvertion(non_reg_json_file_path,
                                            project_execution_summary_json,
                                            'html_structure.html',
                                            html_report_location + '/Non_Regression_TestCase_Report.html')
    except:
        traceback.print_exc()

if __name__ == "__main__":
    reg_json_file_path = sys.argv[1]
    non_reg_json_file_path = sys.argv[2]
    project_execution_summary_json = sys.argv[3]
    html_report_location = sys.argv[4]

    html_report(reg_json_file_path, non_reg_json_file_path, project_execution_summary_json, html_report_location)
