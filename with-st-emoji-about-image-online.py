# streamlit run with-st-emoji-about-image-online.py

import streamlit as st
import time

# 엘리베이터 정보 정의
left_elevators = [[1, 5, 9], [1, 7, 12, 13, 14, 15]]
right_elevators = [[1, 11], [1, 5, 8], [1, 6, 10]]
elevators = left_elevators + right_elevators

# 피로도 점수 계산 함수
def calculate_fatigue(steps, going_up=True):
    if going_up:
        return steps * 1.5
    else:
        return steps

# 최적 경로 탐색 함수
def find_optimal_path_with_transfers(start, end):
    optimal_score = float('inf')
    optimal_steps = []

    def search_path(current_path, current_score, current_floor, target_floor, visited):
        nonlocal optimal_score, optimal_steps

        if current_floor == target_floor:
            if current_score < optimal_score:
                optimal_score = current_score
                optimal_steps = current_path[:]
            return

        for elevator_index, elevator in enumerate(elevators):
            if current_floor in elevator:
                for next_floor in elevator:
                    if next_floor not in visited:
                        visited.add(next_floor)
                        transfer = ""
                        if next_floor != current_floor:
                            if elevator_index < len(left_elevators):
                                transfer = "Trans_to_Left_EV"
                            else:
                                transfer = "Trans_to_Right_EV"
                        if next_floor == target_floor:
                            search_path(current_path + [transfer, next_floor], current_score, next_floor, target_floor, visited)
                        else:
                            search_path(current_path + [transfer, next_floor], current_score, next_floor, target_floor, visited)
                        visited.remove(next_floor)

        for direction in [-1, 1]:
            next_floor = current_floor + direction
            if 1 <= next_floor <= 15 and next_floor not in visited:
                visited.add(next_floor)
                additional_score = calculate_fatigue(1, going_up=direction > 0)
                search_path(current_path + ["Trans_to_Stairs", next_floor], current_score + additional_score, next_floor, target_floor, visited)
                visited.remove(next_floor)

    search_path(["Start", start], 0, start, end, {start})
    
    # 연속된 Trans_to_Stairs 제거 로직 추가
    compressed_steps = []
    i = 0
    while i < len(optimal_steps):
        if optimal_steps[i] == "Trans_to_Stairs":
            start_stair = optimal_steps[i-1]
            while i < len(optimal_steps) and optimal_steps[i] == "Trans_to_Stairs":
                i += 2
            end_stair = optimal_steps[i-1]
            compressed_steps.append("Trans_to_Stairs")
            compressed_steps.append(end_stair)
        else:
            compressed_steps.append(optimal_steps[i])
            i += 1
    
    return compressed_steps[1:], optimal_score

# Streamlit 인터페이스 설정
st.title("북악관 엘베 최적 경로 계산기 ⛰️ 🏢 🛗")

# Expander 사용하여 팝업 형태로 정보 제공
with st.expander("이 프로그램은 대체 뭔가요?"):
    st.image('https://cdn.discordapp.com/attachments/1246482912417681512/1246483030722478141/ev.jpeg?ex=665c8d49&is=665b3bc9&hm=e1b736d2c3cc7aea8be25a4748e338d18b29e1e3e0a39703b84cac5b0fe22c83&', caption='북악관 엘리베이터 현황 : 보통은 고층부, 저층부지만 북악관은..')
    st.markdown("북악관에는 각기 다른 층만 운행하는 엘리베이터가 5개나 있어서 갈아타기가 헷갈릴 수 있죠. 이 프로그램은 출발층과 도착층을 입력하면 가장 빠르고 편한 경로를 찾아줘요. 이제 어디서든 쉽게 이동하세요!")

# 사용자 입력 받기
start_floor = st.slider("출발 층", 1, 15, 1)
end_floor = st.slider("도착 층", 1, 15, 1)

if st.button("최적 경로 계산"):
    with st.spinner('계산중...'):
        time.sleep(2)
        optimal_path_with_transfers, fatigue_score_with_transfers = find_optimal_path_with_transfers(start_floor, end_floor)

    # 결과 출력
    result_steps = optimal_path_with_transfers
    result2_parts = [f"(출발){result_steps[0]}"]
    for i in range(1, len(result_steps), 2):
        result2_parts.append(f"({result_steps[i]}){result_steps[i+1]}")
    result2_parts.append(f"(End){end_floor}")
    result2 = "->".join(result2_parts)

    label_map = {
        "Start": "출발",
        "Trans_to_Right_EV": "건물 오른쪽 EV",
        "Trans_to_Left_EV": "건물 왼쪽 EV",
        "Trans_to_Stairs": "계단"
    }

    prev_floor = start_floor
    for part in result2_parts[:-1]:
        label, value = part.strip("()").split(")")
        current_floor = int(value)
        if label == "출발":
            st.metric(label=f"{current_floor}F", value="출발 📍")
        elif label == "End":
            st.metric(label=f"{current_floor}F", value="도착 📍")
        else:
            translated_label = label_map.get(label, label)
            if translated_label in ["건물 오른쪽 EV", "건물 왼쪽 EV"]:
                st.metric(label=translated_label, value=f"{prev_floor}F → {current_floor}F 로 이동 🛗")
            elif translated_label == "계단":
                direction = "올라가기" if current_floor > prev_floor else "내려가기"
                st.metric(label=translated_label, value=f"{current_floor}F 로 {direction} 🚶")
            prev_floor = current_floor
        st.write("↓")
    
    # 마지막 도착 층 표시 (화살표 없이)
    label, value = result2_parts[-1].strip("()").split(")")
    st.metric(label=f"{value}F", value="도착 📍")
