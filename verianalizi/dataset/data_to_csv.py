from scipy.io import loadmat
import os
import pandas as pd


def load_data(mat_path, battery, status):
    mat = loadmat(mat_path)
    counter = 0
    dataset = []

    for i in range(len(mat[battery][0, 0]["cycle"][0])):
        row = mat[battery][0, 0]["cycle"][0, i]
        if row["type"][0] == status:
            ambient_temperature = row["ambient_temperature"][0][0]
            data = row["data"]
            capacity = data[0][0]["Capacity"][0][0]
            for j in range(len(data[0][0]["Voltage_measured"][0])):
                voltage_measured = data[0][0]["Voltage_measured"][0][j]
                current_measured = data[0][0]["Current_measured"][0][j]
                temperature_measured = data[0][0]["Temperature_measured"][0][j]
                current_load = data[0][0]["Current_load"][0][j]
                voltage_load = data[0][0]["Voltage_load"][0][j]
                time = data[0][0]["Time"][0][j]
                dataset.append(
                    [
                        counter + 1,
                        ambient_temperature,
                        capacity,
                        voltage_measured,
                        current_measured,
                        temperature_measured,
                        current_load,
                        voltage_load,
                        time,
                    ]
                )
            counter = counter + 1

    return pd.DataFrame(
        data=dataset,
        columns=[
            "cycle",
            "ambient_temperature",
            "capacity",
            "voltage_measured",
            "current_measured",
            "temperature_measured",
            "current_load",
            "voltage_load",
            "time",
        ],
    )


datasets = ["B0005", "B0006", "B0018"]
status = "discharge"
for name in datasets:
    dataset = load_data(f"{name}.mat", name, status="discharge")

    csv_filename = f"{name}_{status}.csv"
    dataset.to_csv(csv_filename, index=False)
