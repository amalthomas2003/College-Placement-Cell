
import re
date_pattern = r'\d{4}-\d{2}-\d{2}'  # Regular expression pattern for 'yyyy-mm-dd' format
company_list=['tcs','wipro','infosys']  #update the name of recruting companies, automatically reflected in company hr userid
branch_list=["CU","ME","EE","CE","IT","AE","EC","AD","CS"]
# Check if a date string matches the 'yyyy-mm-dd' format
def is_valid_date(date_string):
    return bool(re.match(date_pattern, date_string))

def student_userid_ends_with():
    return 'rajagiri.edu.in' #update to change student_userid ending string


def admin_userid_ends_with():
    return 'rajagiri.admin.in' #update to change admin_userid ending string


def company_hr_userid_ends_with():
    company_list=['tcs','wipro','infosys']  #update the name of recruting companies, automatically reflected in company hr userid
    updated_company_list=['@'+x+'.in' for x in company_list]
    return updated_company_list

def default_cgpa():
    return 7                #if the company doesn't specify a min_cgpa while updating requiremtns


def default_dob():
    return "2003-01-01"         #if the company doesn't specify a max_dob while updating requiremtns


def choose_rank(cc_points):
    if cc_points<5:
        return ['Arial, sans-serif',' #6DB7AC','','','18px']#black
    elif cc_points<10:
        return ['Roboto, sans-serif','#E75480','','bold','21px']#rose
    elif cc_points<15:
        return ['Lato, sans-serif','#008000','','bold','21px']#green
    elif cc_points<20:
        return ['Courier New, monospace','#8A2BE2','italic','bold','26px']#violet

    else:
        return ['Georgia, serif',' #FF0000','italic','bold','23px']#red

#question id generator function
def q_prefix():
    return "AM"
def q_suffix():
    return "AL"

