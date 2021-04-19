ACTIVITY_PROFILE_DICT = dict({'go swimming': [25,100], 'go hiking': [10,100], \
        'go to the tide pooltide': [10,100], 'take a scenic drive': [0,100],  \
        'do indoor maintenance chores': [-20,100], 'go to a movie': [0,100],  \
        'go bowling': [0,100], 'play card games': [0,100],                    \
        'do garage maintenance': [0,2]})

# iterate through the first four incices of each activity in the activity_profile_dict,
# add them together, and compare the sum to the first value in the first index of the
# profile_now_list list object.
def compare_activity_temp(x):
    activity_message = []    
    for key in x:
        if x.get(key)[0] <= 2 and x.get(key)[1] >= 2:
                activity_message.append(key)  
    return(activity_message)

def main():
    
    print(compare_activity_temp(ACTIVITY_PROFILE_DICT))

main()    