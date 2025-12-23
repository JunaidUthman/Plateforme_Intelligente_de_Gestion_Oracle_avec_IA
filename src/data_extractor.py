import pandas as pd
import os
from datetime import datetime

class OracleSimulator:
    def __init__(self, output_dir='data'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        print(f"🚀 Simulateur Oracle initialisé (Version Détaillée).")

    def generate_audit_logs(self):
        """Simule AUD$ avec des patterns d'anomalies réels (Module 6) [cite: 48, 115, 243]"""
        data = [
            # Activité normale
            {"TIMESTAMP": "2026-01-13 09:00:00", "USER": "HR_APP", "ACTION": "SELECT", "OBJECT": "EMPLOYEES", "STATUS": "SUCCESS", "OS_USER": "web_srv", "TERMINAL": "T1"},
            # Tentative suspecte : Hors heures de bureau
            {"TIMESTAMP": "2026-01-13 03:15:00", "USER": "SYS", "ACTION": "LOGON", "OBJECT": "DATABASE", "STATUS": "SUCCESS", "OS_USER": "unknown", "TERMINAL": "Remote"},
            # Pattern d'injection SQL
            {"TIMESTAMP": "2026-01-13 14:20:10", "USER": "APP_USER", "ACTION": "SELECT", "OBJECT": "USERS' OR '1'='1", "STATUS": "FAILED", "OS_USER": "attacker", "TERMINAL": "UNK"},
            # Escalade de privilège
            {"TIMESTAMP": "2026-01-13 16:45:00", "USER": "GHOST_USER", "ACTION": "GRANT", "OBJECT": "DBA ROLE", "STATUS": "SUCCESS", "OS_USER": "admin_guest", "TERMINAL": "T2"}
        ]
        pd.DataFrame(data).to_csv(f"{self.output_dir}/audit_logs.csv", index=False)
        print("✅ audit_logs.csv généré (avec patterns d'attaques).")

    def generate_security_config(self):
        """Simule DBA_USERS et PROFILES détaillés (Module 4) [cite: 50, 83, 87]"""
        data = [
            {
                "USERNAME": "SYS", "ACCOUNT_STATUS": "OPEN", "ROLE": "DBA", 
                "FAILED_LOGIN_ATTEMPTS": 0, "PASSWORD_LIFE_TIME": "UNLIMITED", # Risque critique
                "PROFILE": "DEFAULT", "LAST_LOGIN": "2026-01-13 08:00"
            },
            {
                "USERNAME": "HR_APP", "ACCOUNT_STATUS": "OPEN", "ROLE": "CONNECT, RESOURCE", 
                "FAILED_LOGIN_ATTEMPTS": 5, "PASSWORD_LIFE_TIME": 90, # Bonne pratique
                "PROFILE": "APP_PROFILE", "LAST_LOGIN": "2026-01-13 09:30"
            },
            {
                "USERNAME": "GHOST_USER", "ACCOUNT_STATUS": "OPEN", "ROLE": "DBA", 
                "FAILED_LOGIN_ATTEMPTS": 10, "PASSWORD_LIFE_TIME": "UNLIMITED", # Risque majeur
                "PROFILE": "DEFAULT", "LAST_LOGIN": "2026-01-12 23:45"
            }
        ]
        pd.DataFrame(data).to_csv(f"{self.output_dir}/security_config.csv", index=False)
        print("✅ security_config.csv généré (avec paramètres de profils).")

    def generate_performance_metrics(self):
        """Simule V$SQLSTAT et Plans d'exécution (Module 5) [cite: 49, 51, 99, 107]"""
        data = [
            {
                "SQL_ID": "sql_slow_001",
                "SQL_TEXT": "SELECT * FROM SALES WHERE REGION = 'NORTH' AND YEAR = 2024",
                "ELAPSED_TIME": 15000, "CPU_TIME": 14500, "EXECUTIONS": 1,
                "DISK_READS": 80000, "OPTIMIZER_COST": 4500,
                "PLAN_OPERATION": "TABLE ACCESS FULL", # Cause de lenteur
                "OBJECT_NAME": "SALES", "OPTIONS": "FULL SCAN"
            },
            {
                "SQL_ID": "sql_fast_002",
                "SQL_TEXT": "SELECT name FROM EMPLOYEES WHERE emp_id = 500",
                "ELAPSED_TIME": 10, "CPU_TIME": 8, "EXECUTIONS": 100,
                "DISK_READS": 2, "OPTIMIZER_COST": 2,
                "PLAN_OPERATION": "INDEX UNIQUE SCAN", # Optimal
                "OBJECT_NAME": "EMP_PK", "OPTIONS": "BY INDEX"
            }
        ]
        pd.DataFrame(data).to_csv(f"{self.output_dir}/performance_metrics.csv", index=False)
        print("✅ performance_metrics.csv généré (avec détails des plans).")

    def run_all(self):
        self.generate_audit_logs()
        self.generate_security_config()
        self.generate_performance_metrics()
        print("\n🏆 Module 1 terminé : Données enrichies prêtes pour l'IA.")

if __name__ == "__main__":
    simulator = OracleSimulator()
    simulator.run_all()