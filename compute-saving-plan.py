import requests
import csv

# def InputMenu():
#     print("************MAIN MENU**************")
#     spChoice = input("""
#                       1: ComputeSavingsPlans
#                       2: EC2InstanceSavingsPlans

#                       Please enter your choice: """)
#     if spChoice == "1":
#         spType = "ComputeSavingsPlans"
#     elif spChoice == "2":
#         spType = "EC2InstanceSavingsPlans"
#     else:
#         print("You must only select either 1 or 2")
#         print("Please try again")
#         InputMenu()
#     return spType

def GenURL( InstanceType, Location, OS ):
    baseURL='https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-instance-savings-plan-ec2-calc/'
    if OS == 'Windows (Amazon VPC)':
        platform = 'Windows/NA'
    elif OS == 'Linux/UNIX':
        platform = 'Linux/NA'
    elif OS == 'Windows with SQL Server Enterprise':
        platform = 'Windows/SQL%20Ent'
    elif OS == 'Windows with SQL Server Standard':
        platform = 'Windows/SQL%20Std'
    elif OS == 'Windows with SQL Server Web':
        platform = 'Windows/SQL%20Web'
    else:
        platform = OS
   
    URL= baseURL + InstanceType + '/' + Location + '/' + platform + '/Shared/index.json'
    finalURL = URL.replace(" ", "%20")
    return finalURL
    # print(finalURL)

def main():
    spType = "ComputeSavingsPlans"
    spEffectiveHourlyRate = 0
    odEffectiveHourlyRate = 0
    totalUpfrontCost = 0
    # print(spType)
    with open('ec2-recommendations.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            InstanceType = row['Instance Type']
            Location = row['Location']
            OS = row['OS']
            paymentOption = row['Payment Option'].replace("_", " ")
            term = row['Term'] + " year"
            qantity = int(row['Recommended Instance Quantity Purchase'])
            url = GenURL(InstanceType, \
                Location, \
                OS)
            # print(url)
            resp = requests.get(url)
            statuCode = resp.status_code
            if statuCode == 200:
                respJSON = resp.json()
                # print(respJSON["regions"]["Asia Pacific (Sydney)"]["ComputeSavingsPlans 3 year No Upfront"]["ec2:PricePerUnit"])
                odPricePerUnit = float(respJSON["regions"][Location][spType + " " + term + " " + paymentOption]["ec2:PricePerUnit"])
                dPricePerUnit = float(respJSON["regions"][Location][spType + " " + term + " " + paymentOption]["price"])
                if paymentOption == "No Upfront":
                    upfrontCost = 0
                elif paymentOption == "Partial Upfront":
                    upfrontCost = (odPricePerUnit * qantity * 24 * 365 * int(row['Term']))/2
                elif paymentOption == "Full Upfront":
                    upfrontCost = (odPricePerUnit * qantity * 24 * 365 * int(row['Term']))
                else:
                    print("wrong payment option")
                    break
                odPrice = odPricePerUnit * qantity
                dPrice = dPricePerUnit * qantity
                # print('On Demand Price :', odPrice)
                # print('Discount Price :', dPrice)
                print(upfrontCost)
                print('.')
                spEffectiveHourlyRate = spEffectiveHourlyRate + dPrice
                odEffectiveHourlyRate = odEffectiveHourlyRate + odPrice
                totalUpfrontCost = totalUpfrontCost + upfrontCost
            else:
                print("one or more api request failed")
                break

    print('Compute Savings Plan Effective Hourly Rate: $',spEffectiveHourlyRate)
    print('Compute Savings Plan Upfront Cost: $',totalUpfrontCost)
    print('Compute Savings Plan Total Cost: $', spEffectiveHourlyRate * 24 * 365 * int(row['Term']))
    print('Compute Savings Plan Average saving: ', (1 - spEffectiveHourlyRate/odEffectiveHourlyRate)*100, '%')
    print("-------------------------------------")
    print('On Demand Hourly Price: $',odEffectiveHourlyRate)
    print('On Demand Total Cost: $', odEffectiveHourlyRate * 24 * 365 * int(row['Term']))

main()