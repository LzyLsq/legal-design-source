import sys
from pathlib import Path

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "shared").is_dir())))

from shared import config, web  # noqa: E402

from flask import render_template, jsonify

app = web.create_flask_app(__name__)


def get_db_connection():
    return config.connect_pymysql()

@app.route('/')
def index():
    return render_template('feedback_b.html')

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM feedback_b ORDER BY create_time DESC"
            cursor.execute(sql)
            feedback_list = cursor.fetchall()

            for feedback in feedback_list:
                if 'create_time' in feedback:
                    feedback['create_time'] = feedback['create_time'].strftime('%Y-%m-%d %H:%M:%S')
                if 'update_time' in feedback:
                    feedback['update_time'] = feedback['update_time'].strftime('%Y-%m-%d %H:%M:%S') if feedback['update_time'] else None

        return jsonify({'code': 200, 'data': feedback_list, 'message': 'success'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})
    finally:
        if connection:
            connection.close()

@app.route('/api/feedback/<int:feedback_id>', methods=['GET'])
def get_feedback_detail(feedback_id):
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM feedback_b WHERE id = %s"
            cursor.execute(sql, (feedback_id,))
            feedback = cursor.fetchone()

            if feedback:
                if 'create_time' in feedback:
                    feedback['create_time'] = feedback['create_time'].strftime('%Y-%m-%d %H:%M:%S')
                if 'update_time' in feedback:
                    feedback['update_time'] = feedback['update_time'].strftime('%Y-%m-%d %H:%M:%S') if feedback['update_time'] else None

                return jsonify({'code': 200, 'data': feedback, 'message': 'success'})
            return jsonify({'code': 404, 'message': 'Feedback not found'})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})
    finally:
        if connection:
            connection.close()

@app.route('/api/feedback/<int:feedback_id>/mark', methods=['POST'])
def mark_feedback(feedback_id):
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE feedback_b SET is_processed = 1, update_time = NOW() WHERE id = %s"
            cursor.execute(sql, (feedback_id,))
            connection.commit()
            return jsonify({'code': 200, 'message': 'Marked as processed'})
    except Exception as e:
        if connection:
            connection.rollback()
        return jsonify({'code': 500, 'message': str(e)})
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    web.run_flask(app, 5033)