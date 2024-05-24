# import statements:
import json
import collections
import matplotlib.pyplot as plt

# Left Join method
def left_join(left_table, right_table, on='user_id'):
    # Create a dictionary from the right table using the join key for quick lookup
    right_dict = {item[on]: item for item in right_table}
    
    # Initialize the result list
    joined_table = []
    
    # Iterate over each record in the left table
    for left_item in left_table:
        # Get the corresponding record from the right table
        right_item = right_dict.get(left_item[on], {})
        
        # Merge two dictionaries, prioritizing values from the left item
        merged_item = {**right_item, **left_item}
        
        # Append the merged record to the result list
        joined_table.append(merged_item)
        
    return joined_table

# Task 2: Calculate Spam Rates

# a) Global Spam Rate by User Count:
def spam_rate_by_user_count(users):
    total_users = len(users)
    spam_users = sum(1 for user in users if user['is_spam'] == 1)
    return spam_users / total_users

# b) Global Spam Rate by Event Count
def spam_rate_by_event_count(events, users):
    user_spam_dict = {user['user_id']: user['is_spam'] for user in users}
    total_events = len(events)
    spam_events = sum(1 for event in events if user_spam_dict.get(event['user_id'], 0) == 1)
    return spam_events / total_events

# c) Spam Rate by Event Count for Top Five Email Domains
def spam_rate_by_email_domain(events, users):
    from collections import defaultdict, Counter
    
    user_spam_dict = {user['user_id']: user['is_spam'] for user in users}
    domain_spam_counts = defaultdict(lambda: [0, 0])  # [spam_count, total_count]

    for user in users:
        domain = user['email_domain']
        domain_spam_counts[domain][0] += user_spam_dict[user['user_id']]
        domain_spam_counts[domain][1] += 1

    spam_rates = {domain: count[0] / count[1] for domain, count in domain_spam_counts.items()}
    top_five_domains = Counter(spam_rates).most_common(5)
    return top_five_domains

# d) Spam Rate by User Country
def spam_rate_by_user_country(users):
    country_spam_counts = collections.defaultdict(lambda: [0, 0])  # [spam_count, total_count]

    for user in users:
        country = user['user_country']
        is_spam = user['is_spam']
        country_spam_counts[country][0] += is_spam
        country_spam_counts[country][1] += 1

    spam_rates = {country: count[0] / count[1] for country, count in country_spam_counts.items()}
    return spam_rates

# e) Spam Rate When Currency and User Country Do Not Match
def spam_rate_currency_mismatch(users):
    mismatch_count = sum(1 for user in users if user['currency_country'] != user['user_country'] and user['is_spam'] == 1)
    total_mismatch = sum(1 for user in users if user['currency_country'] != user['user_country'])
    return mismatch_count / total_mismatch if total_mismatch > 0 else 0

# Method to call all sapm rate calculation methods:

def calculate_all_spam_rates(events, users):
    # Calculate global spam rate by user count
    global_spam_rate_users = spam_rate_by_user_count(users)
    
    # Calculate global spam rate by event count
    global_spam_rate_events = spam_rate_by_event_count(events, users)
    
    # Calculate spam rate by event count for the top five email domains
    top_five_domains_spam_rates = spam_rate_by_email_domain(events, users)
    
    # Calculate spam rate by user country
    spam_rate_countries = spam_rate_by_user_country(users)
    
    # Calculate spam rate for currency and user country mismatch
    spam_rate_currency_mismatch_rate = spam_rate_currency_mismatch(users)
    
    return {
        "Global Spam Rate by User Count": global_spam_rate_users,
        "Global Spam Rate by Event Count": global_spam_rate_events,
        "Top Five Email Domains Spam Rates": top_five_domains_spam_rates,
        "Spam Rate by User Country": spam_rate_countries,
        "Spam Rate for Currency and User Country Mismatch": spam_rate_currency_mismatch_rate
    }

# Load the data from JSON files
with open('event_data.json', 'r') as fh:
    event_data = json.load(fh)
    print("Event Data row 0:", event_data[0])

with open('user_data.json', 'r') as fh:
    user_data = json.load(fh)
    print("User Data row 0:", user_data[0])

    # Performing the left join
merged_data = left_join(event_data, user_data, 'user_id')


# Add 'currency_mismatch' to each event in merged_data
for event in merged_data:
    event['currency_mismatch'] = (event['user_country'] != event['currency_country'])
    
# Specify the filename where you want to store the data
filename = 'merged_data.json'

# Open a file in write mode and use json.dump() to write the data
with open(filename, 'w') as file:
    json.dump(merged_data, file, indent=4)  # 'indent' for pretty-printing

print(f"Merged data has been saved to {filename}.")

# Print the first few joined rows to verify
for data in merged_data[:3]:  # change this slice as necessary to check more/less data
    print(data)

# Calling the calculate the spam rates method
results = calculate_all_spam_rates(event_data, user_data)

# Print the results
for key, value in results.items():
    print(f"{key}: {value}")

# 3) Calculations on feature distributions.
# a) Read through the provided column names. Choose at least three features that
# you think might be indicative of spam using your best guess as to their meanings.
# Explain why you believe they may be indicative of spam.

# Solution:
# a) Selection and Explanation of Features
# 	1.	Email Domain (email_domain): The spam rates for the top five email domains show that certain domains have a high incidence of spam (some even 100%). This indicates that spam may be concentrated in specific domains which are either less regulated or more prone to misuse.
# 	2.	User Country (user_country): The spam rate varies significantly by country, with some countries having a much higher spam rate than others. This could reflect differences in regulation, the prevalence of technology, or cultural factors influencing spam behavior.
# 	3.	Currency and User Country Mismatch: A higher spam rate in cases where the currency does not match the user’s country could indicate misuse, as spammers might prefer to register under different countries to avoid detection or capitalize on currency exchange rates.

# b) Make a plot of the distribution of each chosen column for spam events and
# non-spam events.

# # Solution
# b) Plotting Feature Distributions
# method to plot feature distributions:  
def plot_filtered_feature_distribution(user_data, event_data, feature, title, threshold=10):
    # Using the custom left_join function
    merged_data = left_join(event_data, user_data, 'user_id')
    
    # Initialize counts
    feature_counts = {}
    for item in merged_data:
        if feature in item:
            feature_value = item[feature]
            spam_key = (feature_value, 'Spam')
            non_spam_key = (feature_value, 'Non-Spam')
            if spam_key not in feature_counts:
                feature_counts[spam_key] = 0
            if non_spam_key not in feature_counts:
                feature_counts[non_spam_key] = 0
            if item['is_spam'] == 1:
                feature_counts[spam_key] += 1
            else:
                feature_counts[non_spam_key] += 1

    # Filter features based on total counts across spam and non-spam
    total_counts = {}
    for (f, _), count in feature_counts.items():
        if f in total_counts:
            total_counts[f] += count
        else:
            total_counts[f] = count
    
    significant_features = {f for f, count in total_counts.items() if count > threshold}
    
    # Prepare for plotting
    labels = sorted(significant_features)
    spam_counts = [feature_counts[(f, 'Spam')] for f in labels]
    non_spam_counts = [feature_counts[(f, 'Non-Spam')] for f in labels]
    
    # Plotting
    x = range(len(labels))
    width = 0.35
    
    plt.figure(figsize=(max(12, len(labels) * 0.5), 8))
    plt.bar(x, spam_counts, width, label='Spam', color='r')
    plt.bar([p + width for p in x], non_spam_counts, width, label='Non-Spam', color='b')
    
    plt.xlabel(feature)
    plt.ylabel('Count')
    plt.title(title)
    plt.xticks([p + width / 2 for p in x], labels, rotation=90)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Note on omitted data
    missing_data_count = len(total_counts) - len(significant_features)
    if missing_data_count > 0:
        print(f"Note: {missing_data_count} {feature} with fewer than {threshold} occurrences were not plotted.")

# Example usage
plot_filtered_feature_distribution(user_data, event_data, 'email_domain', 'Distribution of Email Domains by Spam Status')
plot_filtered_feature_distribution(user_data, event_data, 'user_country', 'Distribution of User Country by Spam Status')

# c) Usefulness for Policy and Criteria Selection

# 	1.	Email Domain: This feature is likely useful for a policy, given the clear variance in spam rates across domains. Criteria: A policy might flag events from domains with a historical spam rate exceeding 50% as suspicious.
# 	2.	User Country: Also likely useful due to varying spam rates by country. Criteria: Events from countries with a spam rate over 25% could be subjected to additional scrutiny.
# 	3.	Currency and User Country Mismatch: Given the higher spam rate for mismatches, this feature is useful. Criteria: Any event where the currency does not match the user country might be flagged for further verification.

# Code to Calculate Feature Distributions:
# Initialize dictionaries to count occurrences
domain_spam = collections.defaultdict(int)
domain_non_spam = collections.defaultdict(int)
country_spam = collections.defaultdict(int)
country_non_spam = collections.defaultdict(int)
currency_mismatch_spam = collections.defaultdict(int)
currency_mismatch_non_spam = collections.defaultdict(int)

# Populate the dictionaries
for event in merged_data:
    if event['is_spam']:
        domain_spam[event['email_domain']] += 1
        country_spam[event['user_country']] += 1
        if event['currency_mismatch']:
            currency_mismatch_spam[True] += 1
    else:
        domain_non_spam[event['email_domain']] += 1
        country_non_spam[event['user_country']] += 1
        if event['currency_mismatch']:
            currency_mismatch_non_spam[True] += 1

def calculate_spam_rates(spam_counts, total_counts):
    return {key: spam_counts.get(key, 0) / total for key, total in total_counts.items()}

def calculate_performance_statistics(merged_data, domain_spam_rates, country_spam_rates, currency_mismatch_rate, domain_threshold, country_threshold, mismatch_threshold):
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    
    # Apply the spam detection policy
    for event in merged_data:
        predicted_spam = (domain_spam_rates.get(event['email_domain'], 0) > domain_threshold) or \
                         (country_spam_rates.get(event['user_country'], 0) > country_threshold) or \
                         (event['currency_mismatch'] and currency_mismatch_rate[True] > mismatch_threshold)
        
        actual_spam = event['is_spam'] == 1
        
        if predicted_spam and actual_spam:
            true_positives += 1
        elif predicted_spam and not actual_spam:
            false_positives += 1
        elif not predicted_spam and not actual_spam:
            true_negatives += 1
        elif not predicted_spam and actual_spam:
            false_negatives += 1

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    accuracy = (true_positives + true_negatives) / len(merged_data)

    return {
        'Precision': precision,
        'Recall': recall,
        'Accuracy': accuracy
    }

# Calculate total counts for domains and countries
total_domain_counts = {key: domain_spam[key] + domain_non_spam.get(key, 0) for key in set(domain_spam.keys()).union(domain_non_spam.keys())}
total_country_counts = {key: country_spam[key] + country_non_spam.get(key, 0) for key in set(country_spam.keys()).union(country_non_spam.keys())}

# Calculate spam rates
domain_spam_rates = calculate_spam_rates(domain_spam, total_domain_counts)
country_spam_rates = calculate_spam_rates(country_spam, total_country_counts)

# Example thresholds
domain_threshold = 0.5
country_threshold = 0.2
mismatch_threshold = 0.2

# Calculate performance statistics
performance_stats = calculate_performance_statistics(merged_data, domain_spam_rates, country_spam_rates, currency_mismatch_spam, domain_threshold, country_threshold, mismatch_threshold)
print(performance_stats)


# Proportion Calculation Example:
# Calculate the spam rate for each domain
domain_spam_rates = {domain: domain_spam[domain] / (domain_spam[domain] + domain_non_spam.get(domain, 1))
                     for domain in domain_spam}
country_spam_rates = {country: country_spam[country] / (country_spam[country] + country_non_spam.get(country, 1))
                     for country in country_spam}
currency_mismatch_spam_rates = {currency_mismatch: currency_mismatch_spam[currency_mismatch] / (currency_mismatch_spam[currency_mismatch] + currency_mismatch_non_spam.get(currency_mismatch, 1))
                     for currency_mismatch in currency_mismatch_spam}

print("domain_spam_rates:",domain_spam_rates)
print("country_spam_rates:",country_spam_rates)
print("currency_mismatch_spam_rates:",currency_mismatch_spam_rates)

# 4a) Propose a Spam Policy

# Initial Policy Proposal:

# 	•	Email Domain: Flag events where the email_domain has a spam rate greater than 50%. Domains such as pqvtozksgm.com (93.1%), tnpakdietc.com (85.7%), and cnigzfupuu.com (75%) would be flagged.
# 	•	User Country: Flag events where the user_country has a spam rate greater than 20%. Countries like EGK (99.1%), YHA (93.75%), and AEZ (60%) would be flagged.
# 	•	Currency and Country Mismatch: Flag events where there is a currency and country mismatch, given the overall spam rate for mismatches is 20.6%, which is significantly higher than the average spam rate.

# Performance Statistics to Calculate:

# 	•	Precision: Proportion of events flagged as spam that are truly spam.
# 	•	Recall: Proportion of actual spam events that were correctly identified.
# 	•	Accuracy: Overall proportion of correct predictions.

# To calculate these metrics, we would typically set up a test where we apply these rules to a separate set of data where spam outcomes are known, and then tally up true positives, false positives, true negatives, and false negatives.

# 4b) Adjust the Policy

# If the initial metrics reveal a high number of false positives (low precision), consider adjusting the thresholds to be stricter. For instance:

# 	•	Adjustment: Increase the threshold for email_domain from 50% to 70%. This means only domains with a very high likelihood of being spammy are flagged.

# Goal of Adjustment: Improve precision without significantly sacrificing recall. The idea is to reduce the burden on event moderators or automated systems in dealing with false positives.

# Evaluate Adjustment:
# Recalculate the performance metrics. If the precision improves and recall remains reasonable, then the adjustment is successful. This can be done by applying the adjusted rules to the same test set and comparing the new results to the initial metrics.

# 4c) Strengths and Weaknesses

# Strengths:

# 	•	The policy uses data-driven thresholds to target high-risk categories effectively.
# 	•	It’s flexible, allowing for adjustments based on actual performance metrics.
# 	•	Focuses on multiple features, which helps in capturing different types of spam behavior.

# Weaknesses:

# 	•	It might still miss new or emerging spam trends not represented in the historical data.
# 	•	Could inadvertently flag legitimate events, especially from new users or less common countries, which could harm user experience and trust.
# 	•	Relies heavily on past data, which might not accurately predict future behavior especially in dynamic environments.

# Different Approaches in a Real-World Scenario:

# 	•	Machine Learning: Implement machine learning models that can learn from a broad set of features and adapt over time as new data comes in.
# 	•	Continuous Feedback: Establish mechanisms to incorporate user feedback and manual review outcomes to continually refine the spam detection algorithms.
# 	•	User Reputation System: Develop a system that adjusts the sensitivity of spam detection based on the historical behavior of the user, providing more leeway to trusted users.

# In real-world applications, a combination of automated systems and manual review is often necessary to maintain a balance between effective spam prevention and minimizing false positives, thereby protecting the user experience while combating fraud and abuse.
