import pandas as pd

def create_excel(energy, saved_yield, filename):

    #dictionary to merge data
    merged_data = {}

    for date, yield_value in saved_yield.items():
        merged_data[date] = {
            'Data' : date,
            'Energia wyprodukowana': yield_value,
            'Energia oddana': energy[date].get('production', 0),
            'Energia pobrana': energy[date].get('consumption', 0),
            'Energia skonsumowana': yield_value-energy[date].get('production', 0)
        }

    #creating dataframe
    df = pd.DataFrame(merged_data)

    #creating excel
    df.to_excel(f'{filename}.xlsx', index=False)