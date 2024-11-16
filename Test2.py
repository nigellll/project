from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import logging

app = Flask(__name__)
CORS(app, resources={r"/get_patient_info": {"origins": "*"}})

logging.basicConfig(level=logging.DEBUG)

# CSV 파일 읽기
try:
    df1 = pd.read_csv("1.환자정보.csv")
    df2 = pd.read_csv("2.환자진단_내역.csv")
    df3 = pd.read_csv("3.검사_처방.csv")  # 검사처방 데이터
    df4 = pd.read_csv("4.약_처방.csv")   # 약처방 데이터
    df5 = pd.read_csv("5.간호정보조사지.csv")  # 간호정보 데이터
    df6 = pd.read_csv("6.환자_주의사항.csv")
    for df in [df1, df2, df3, df4, df5, df6]:
        df.columns = df.columns.str.strip()
except FileNotFoundError:
    print("파일 경로가 올바르지 않습니다.")
    df1 = df2 = df3 = df4 = df5 = df6 = None


def get_patient_info(patient_id, role):
    if any(df is None for df in [df1, df2, df3, df4, df5, df6]):
        return {"error": "필수 데이터 파일이 로드되지 않았습니다."}
    patient_id = int(patient_id) #int 아닐수도
    if not (patient_id in df1['일련번호'].astype(int).values):
        return {"error": "해당 환자 정보가 없습니다."}
    info1 = df1[df1['일련번호'].astype(int) == patient_id]
    info2 = df2[df2['일련번호'].astype(int) == patient_id]
    info3 = df3[df3['일련번호'].astype(int) == patient_id]
    info4 = df4[df4['일련번호'].astype(int) == patient_id]
    info5 = df5[df5['일련번호'].astype(int) == patient_id]
    info6 = df6[df6['일련번호'].astype(int) == patient_id]
    result = {"환자정보": info1[['일련번호', '성별', '사망_여부']].drop_duplicates().to_dict(orient="records")}
    if role == "doctor":
        result["진단내역"] = info2[['진료_입원_일자', '진단_질병_코드', '진단_질병_명']].drop_duplicates().to_dict(orient="records")
        result["검사처방"] = info3[['진료_입원_일자', '검사_항목_코드', '검사_항목_명', '진료_나이', '검사_결과(수치)']].drop_duplicates().to_dict(orient="records")
        result["약처방"] = info4[['진료_입원_일자', '처방_코드','성분_명','처방_일자']].drop_duplicates().to_dict(orient="records")
        result["간호정보"] = info5[['입원_일자', '혈압(수축기)', '혈압(이완기)','고혈압','당뇨','심장질환','뇌졸중','고지혈증','암']].drop_duplicates().to_dict(orient="records")
        result["환자주의사항"] = info6[['Hepatitis B_여부', 'Hepatitis C_여부']].drop_duplicates().to_dict(orient="records")
    elif role == "nurse":
        result["성별"] = info1[['일련번호', '성별']].drop_duplicates().to_dict(orient="records")
        result["간호정보"] = info5[['입원_일자', '혈압(수축기)','혈압(이완기)', '체온', '신장', '체중', '흡연_유무']].drop_duplicates().to_dict(orient="records")
        result["진료나이"] = info2[['진료_나이']].drop_duplicates().to_dict(orient="records")
        result["약처방"] = info4[['처방_일자', '처방_코드', '성분_명']].drop_duplicates().to_dict(orient="records")
    return result

@app.route('/get_patient_info', methods=['GET'])
def get_patient_data():
    app.logger.info("요청 받음: %s", request.args)
    patient_id = request.args.get('patient_id')
    role = request.args.get('role')
    
    if not patient_id or not role:
        app.logger.warning("잘못된 요청: 환자 ID 또는 역할 누락")
        return jsonify({"error": "환자 일련번호와 역할 정보가 필요합니다."}), 400
    
    try:
        result = get_patient_info(patient_id, role)
        app.logger.info("응답 전송: %s", result)
        return jsonify(result)
    except Exception as e:
        app.logger.error("오류 발생: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)