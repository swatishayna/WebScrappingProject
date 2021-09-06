import csv


def write(output_data):
    try:
        with open("D:/data science/ineuron/Project/python project/projectscrapping/reviews.csv", 'a') as f:
            print(output_data)
            f.writelines(output_data)

    except Exception as e:
        print(e)