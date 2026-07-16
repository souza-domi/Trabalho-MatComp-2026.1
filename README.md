# Trabalho-MatComp-2026.1

Reconstrução de Trajetória a Partir de Dados de Aceleração

## Dataset

The experiments in this project were conducted using the **Trolley** subset of the **Oxford Inertial Odometry Dataset (OxIOD)**, developed by the **Department of Computer Science, University of Oxford**.

The trajectory reconstruction algorithm uses the raw data provided in the **imu1** and **vi1** files from the **data4** sequence.

**Official dataset:** http://deepio.cs.ox.ac.uk/

> **Note:** The dataset is **not included** in this repository. Please download it directly from the official OxIOD website.

## Setup

1. Download the **Oxford Inertial Odometry Dataset (OxIOD)** from the official website.

2. From the **Trolley** subset, extract the **data4** sequence.

3. Copy the following raw files into the project's `data` folder:

```text
data/
├── imu1.csv
└── vi1.csv
```

4. If you store the dataset in a different location, update the `DATA_DIR` variable in `leitura.py`:

```python
DATA_DIR = Path("data")
```

For example:

```python
DATA_DIR = Path("C:/Users/YourName/Documents/OxIOD/data4")
```

or

```python
DATA_DIR = Path("/home/username/OxIOD/data4")
```

