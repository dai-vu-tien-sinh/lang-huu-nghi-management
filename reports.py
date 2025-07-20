import pandas as pd
import streamlit as st
from database import Database
from utils import create_chart, generate_pdf_report

class ReportGenerator:
    def __init__(self):
        self.db = Database()

    def generate_student_statistics(self):
        students = self.db.get_students()
        classes = self.db.get_classes()
        
        # Create student data with class information
        student_data = []
        for student in students:
            # Find class information for this student
            class_info = None
            if student.class_id:
                class_info = next((c for c in classes if c.id == student.class_id), None)
            
            student_data.append({
                'id': student.id,
                'full_name': student.full_name,
                'birth_date': student.birth_date,
                'address': student.address,
                'email': student.email,
                'admission_date': student.admission_date,
                'class_id': student.class_id,
                'class_name': class_info.name if class_info else 'Chưa phân lớp',
                'academic_year': class_info.academic_year if class_info else 'N/A',
                'health_status': student.health_status,
                'academic_status': student.academic_status,
                'psychological_status': student.psychological_status,
                'gender': student.gender,
                'phone': student.phone,
                'year': student.year,
                'parent_name': student.parent_name,
                'decision_number': student.decision_number,
                'nha_chu_t_info': student.nha_chu_t_info
            })
        
        df = pd.DataFrame(student_data)

        total_students = len(students)
        health_status_counts = df['health_status'].value_counts()
        academic_status_counts = df['academic_status'].value_counts()
        
        # Class distribution statistics
        class_distribution = df['class_name'].value_counts()

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
        
        class_chart = create_chart(
            class_distribution,
            'bar',
            'Students by Class Distribution'
        )

        return {
            'total_students': total_students,
            'health_chart': health_chart,
            'academic_chart': academic_chart,
            'class_chart': class_chart,
            'class_distribution': class_distribution,
            'student_data': student_data
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
            
            # Prepare class distribution information
            class_info_text = "Phân bố học sinh theo lớp:\n"
            for class_name, count in stats['class_distribution'].items():
                class_info_text += f"- {class_name}: {count} học sinh\n"
            
            data = {
                'Total Students': stats['total_students'],
                'Class Distribution': class_info_text,
                'Report Generated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'health_chart': stats['health_chart'] if include_charts else None,
                'academic_chart': stats['academic_chart'] if include_charts else None,
                'class_chart': stats['class_chart'] if include_charts else None,
                'student_data': stats['student_data']  # Include detailed student data with class info
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