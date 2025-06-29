import pandas as pd
import streamlit as st
from database import Database
from utils import create_chart, generate_pdf_report

class ReportGenerator:
    def __init__(self):
        self.db = Database()

    def generate_student_statistics(self):
        students = self.db.get_students()
        df = pd.DataFrame(students)

        total_students = len(students)
        health_status_counts = df['health_status'].value_counts()
        academic_status_counts = df['academic_status'].value_counts()

        # Create charts
        health_chart = create_chart(
            health_status_counts,
            'pie',
            'Student Health Status Distribution'
        )
        academic_chart = create_chart(
            academic_status_counts,
            'bar',
            'Academic Status Distribution'
        )

        return {
            'total_students': total_students,
            'health_chart': health_chart,
            'academic_chart': academic_chart
        }

    def generate_veteran_statistics(self):
        veterans = self.db.get_veterans()

        # Create list of dictionaries manually
        data = []
        for v in veterans:
            data.append({
                'id': v.id,
                'full_name': v.full_name,
                'birth_date': v.birth_date,
                'service_period': v.service_period,
                'health_condition': v.health_condition,
                'address': v.address,
                'email': v.email,
                'contact_info': v.contact_info
            })

        # Create DataFrame from list of dicts
        df = pd.DataFrame(data)

        total_veterans = len(veterans)
        # Add error handling for empty DataFrame
        if not df.empty and 'health_condition' in df.columns:
            health_condition_counts = df['health_condition'].value_counts()
        else:
            health_condition_counts = pd.Series([])

        health_chart = create_chart(
            health_condition_counts,
            'pie',
            'Veteran Health Condition Distribution'
        )

        return {
            'total_veterans': total_veterans,
            'health_chart': health_chart
        }

    def generate_pdf_summary(self, report_type: str, language: str = "vi", include_charts: bool = True):
        from translations import get_current_language
        
        # Use current language if not specified
        if language is None:
            language = get_current_language()
        
        if report_type == 'students':
            stats = self.generate_student_statistics()
            data = {
                'Total Students': stats['total_students'],
                'Report Generated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'health_chart': stats['health_chart'] if include_charts else None,
                'academic_chart': stats['academic_chart'] if include_charts else None
            }
            return generate_pdf_report(data, 'Student Statistics Report', include_charts, language)

        elif report_type == 'veterans':
            stats = self.generate_veteran_statistics()
            data = {
                'Total Veterans': stats['total_veterans'],
                'Report Generated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'health_chart': stats['health_chart'] if include_charts else None
            }
            return generate_pdf_report(data, 'Veteran Statistics Report', include_charts, language)