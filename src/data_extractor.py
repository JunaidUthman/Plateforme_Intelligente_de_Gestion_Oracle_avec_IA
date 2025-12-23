import pandas as pd
import os
import json
from datetime import datetime, timedelta

class OracleSimulator:
    def __init__(self, output_dir='data'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        print(f"🚀 Simulateur Oracle initialisé. Dossier de sortie : {self.output_dir}")

    def generate_audit_logs(self):
        """Simule la table AUD$ [cite: 48, 243]"""
        data = [
            {"TIMESTAMP": "2026-01-13 08:30:05", "USER": "SYS", "ACTION": "LOGON", "OBJECT": "DATABASE", "STATUS": "SUCCESS"},
            {"TIMESTAMP": "2026-01-13 09:15:20", "USER": "DBA_USER", "ACTION": "SELECT", "OBJECT": "HR.SALARIES", "STATUS": "SUCCESS"},
            {"TIMESTAMP": "2026-01-13 10:00:12", "USER": "APP_WEB", "ACTION": "UPDATE", "OBJECT": "SALES.ORDERS", "STATUS": "SUCCESS"},
            {"TIMESTAMP": "2026-01-13 23:45:00", "USER": "UNKNOWN", "ACTION": "LOGON", "OBJECT": "DATABASE", "STATUS": "FAILED"},
        ]
        df = pd.DataFrame(data)
        df.to_csv(f"{self.output_dir}/audit_logs.csv", index=False)
        print("Fichier audit_logs.csv généré.")

    def generate_security_config(self):
        """Simule DBA_USERS, DBA_ROLES, DBA_SYS_PRIVS [cite: 50, 83]"""
        data = [
            {"USERNAME": "SYS", "ACCOUNT_STATUS": "OPEN", "ROLE": "DBA", "SYS_PRIVILEGE": "ANY PRIVILEGE"},
            {"USERNAME": "HR_APP", "ACCOUNT_STATUS": "OPEN", "ROLE": "CONNECT", "SYS_PRIVILEGE": "CREATE SESSION"},
            {"USERNAME": "SCOTT", "ACCOUNT_STATUS": "EXPIRED", "ROLE": "RESOURCE", "SYS_PRIVILEGE": "NONE"},
            {"USERNAME": "GHOST_USER", "ACCOUNT_STATUS": "OPEN", "ROLE": "DBA", "SYS_PRIVILEGE": "DROP ANY TABLE"},
        ]
        df = pd.DataFrame(data)
        df.to_csv(f"{self.output_dir}/security_config.csv", index=False)
        print(" Fichier security_config.csv généré.")

    def generate_performance_metrics(self):
        """Simule V$SQLSTAT et V$SQL_PLAN [cite: 49, 51, 99]"""
        data = [
            {"SQL_ID": "sql_123", "ELAPSED_TIME": 5000, "CPU_TIME": 4500, "EXECUTIONS": 100, "SQL_TEXT": "SELECT * FROM sales WHERE region = 'North'"},
            {"SQL_ID": "sql_456", "ELAPSED_TIME": 120000, "CPU_TIME": 110000, "EXECUTIONS": 5, "SQL_TEXT": "SELECT * FROM big_table ORDER BY 1, 2, 3"},
        ]
        df = pd.DataFrame(data)
        df.to_csv(f"{self.output_dir}/performance_metrics.csv", index=False)
        print(" Fichier performance_metrics.csv généré.")

    def run_all(self):
        """Exécute toutes les simulations [cite: 44]"""
        self.generate_audit_logs()
        self.generate_security_config()
        self.generate_performance_metrics()
        print("\n🏆 Module 1 terminé : Toutes les données simulées sont prêtes dans /data")

if __name__ == "__main__":
    simulator = OracleSimulator()
    simulator.run_all()