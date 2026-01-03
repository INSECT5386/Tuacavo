from lark import Lark, Transformer, Tree, Token

my_grammar = r"""
    ?start: expressions
    ?expressions: (expression | WS)+
    ?expression: causal_expr | sequence_expr | atom
    ?causal_expr: expression CAUSAL_OP expression | expression DELAYED_OP expression
    ?sequence_expr: expression EN expression | expression COMMA expression | expression JU_TAG expression -> repeated_action
    
    ?atom: (tag_content | grouping) [target] [eth_property] [EXCLAMATION]
         | target [eth_property] [EXCLAMATION]

    ?tag_content: tag_list [NUMBER] [vector_suffix] [bracket_desc]

    grouping: "{" expression "}"                   -> logic_group
            | "[" expression "]"                   -> action_group
            | "(" expression ")"                   -> inner_group

    tag_list: (ID_TAG | TAG_TOKEN | FIT_TAG | CERTAIN_TAG | HUMAN_TAG | NO | QUESTION | SLOT_TAG | R_TAG)+
    bracket_desc: "(" (WORD | TAG_TOKEN | expression) ")"
    target: "@" (ID_TAG | TAG_TOKEN | grouping | WORD | bracket_desc | atom)
    eth_property: "eth" (tag_list | grouping | PIN_TAG | SLOT_TAG | WORD | NUMBER | causal_expr) [bracket_desc]
    
    vector_suffix: VECTOR_TAG [NUMBER] [QUESTION]

    CAUSAL_OP: /(!|-|~)+\s*a'/
    DELAYED_OP: /(!|-|~)+\s*sa'/
    EN: "en"
    COMMA: ","
    NO: "no"
    QUESTION: "?"
    EXCLAMATION: "!" 
    R_TAG: "R"
    JU_TAG: "Ju"

    ID_TAG: "Im" | "Ym" | "Om"
    TAG_TOKEN: /[A-Z][A-Za-z]*/ 
    PIN_TAG: "Pinrdy" | "Pinrun" | "Pinend" | "Pinhold"
    SLOT_TAG: /T\d+/ | "Z" | "T" | "K" | "F" | "N" | "Tp" | "Tf" | "Tn" | "Tef" | "Td" | "Tei"
    VECTOR_TAG: "Pu" | "Mu" | "Cu" | "Xu" | "Su" | "Hu" | "Ru" | "Lu" | "Vu"
    FIT_TAG: "#Burnout" | "#Flow"
    CERTAIN_TAG: "ic" | "ec"
    HUMAN_TAG: "eta" | "ata" | "uta"
    WORD: /[a-zA-Z]+/
    NUMBER: /[0-9]+/

    %import common.WS
    %ignore WS
"""

def Josa(text, josa_type):
    """
    text: 대상 단어 (예: '대학교', '판단')
    josa_type: '을/를', '이/가', '은/는' 중 선택
    """
    if not text: return text
    # 마지막 글자의 유니코드 확인 (받침 유무 판단)
    last_char = text.strip()[-1]
    if not ('가' <= last_char <= '힣'): return text + josa_type.split('/')[1]
    
    has_jongsung = (ord(last_char) - ord('가')) % 28 > 0
    if josa_type == '을/를':
        return text + ('을' if has_jongsung else '를')
    elif josa_type == '이/가':
        return text + ('이' if has_jongsung else '가')
    elif josa_type == '은/는':
        return text + ('은' if has_jongsung else '는')
    return text

class LangTranslator(Transformer):
    def __init__(self):

        self.dict_map = {
                # 1. 인칭 및 기본 주체 (Identity)
                "Im": "내(화자)가 ", "Ym": "네(청자)가 ", "Om": "제3자가 ",
                "Dg": "상급자", "Suba": "하위 객체",

                # 2. 결핍 및 해소 (V-S Series)
                "Va": "결핍", "Vab": "육체적 결핍", "Vam": "정신적 결핍", "Var": "물리적 결핍",
                "Sa": "해소/획득", "Sab": "육체적 해소", "Sam": "정신적 해소", "Sar": "물리적 해소",
                
                # 3. 인지 및 정보 (L Series)
                "La": "지식", "Lam": "기억", "Lai": "정보입력", "Lac": "추론", "Lav": "확인완료",
                "Lia": "데이터", "Liad": "수치 데이터", "Liat": "텍스트 정보", "Liam": "미디어 정보",
                
                # 4. 감정 및 심리 상태 (R-Z Series)
                "Ra": "거부/분노", "Rai": "짜증", "Raf": "공포", "Ras": "슬픔",
                "Za": "평온/수용", "Zas": "휴식", "Zaa": "동의", "Zaf": "충족",
                "Fa": "해상도", "Fam": "집중", 
                "Ena": "에너지", "Enab": "활력",
                "Mita": "의지", "Mitam": "도덕", "Mitat": "의도/목적", "Mitar": "의욕/사기",
                "#Burnout": "번아웃", "#Flow": "몰입",

                # 5. 행동 및 작용 (A Series)
                "Aca": "행동", "Ae": "물리적 행동을 ", "Au": "언어적 행동을 ", "Aa": "조작을 ", "Aeg": "가다", "Aeu": "걷다", "Aefo": "고치다", "Aef": "날다", "Aep": "놀다", "Aeup": "누르다", "Aec": "닫다", "Aes": "달리다", "Ael": "당기다", "Aet": "던지다", "Aek": "돌보다", "Aeir": "돕다", "Aect": "들다", "Aegr": "따라가다", "Aetir": "따라하다", "Aetu": "액체를 따르다", "Aelu": "떨어지다", "Aei": "뛰다", "Aeal": "마시다", "Aem": "만나다", "Aema": "만들다", "Aetou": "만지다", "Aer": "먹다", "Aelr": "밀다", "Aeze":"받다", "Aelo": "보다", "Aebo": "부수다", "Aeop": "서다", "Aeso": "숨다", "Aelit": "쉬다", "Aetur": "심다", "Aeur": "앉다", "Aeun": "없다", "Aein": "있다", "Aecr": "열다", "Aeol": "입다", "Aesl": "자다", "Aekir": "자라다", "Aeku": "자르다", "Aeca": "잡다", "Aeki": "주다", "Ausi": "말하다", "Aues": "읽다", "Auer": "쓰다", "Auli": "듣다", "Aulo": "소리 지르다", "Auls": "속삭이다",
                "Coa": "협력/협동", "Ata": "조언/지도", "Ta": "신뢰/유대", "Exa": "교환/거래",
                "Ka": "충돌/오류", "Pa": "규칙/계약", "Val": "가치", "Has": "소유/연결",

                # 6. 환경 및 장소 (E Series)
                "Egoc": "장소", "Egob": "사물", "Egev": "환경 조건", "Exi": "시스템",
                "Ecuo": "집", "Ecup": "경찰서", "Ecuf": "소방서", "Ecear": "식당", "Eceaf": "카페",
                "Secas": "초등학교", "Mecas": "중학교", "Hecas": "고등학교", "Uecas": "대학교",
                
                # 7. 시간 및 슬롯 (T-S Series)
                "Z": "현재 상황", "T": "시간", "K": "원인", "F": "결과/작용", "N": "가치 판단",
                "Tp": "과거", "Tf": "미래", "Tn": "현재", "Tef": "진행형",
                "rdy": "-대기", "run": "-를 하고있다", "end": "-를 했다.", "hold": "-중단",

                # 8. 성격 및 수치 속성 (Certainty & Human)
                "ic": "확정", "ec": "가변", "no": "안 함/아님", "Ju": "반복", "R": " 은(는) ",
                "eta": "직관", "ata": "공감", "uta": "상상",

                # 9. 벡터 및 변동 (Vector)
                "Pu": "강화", "Mu": "약화", "Cu": "반전", "Xu": "모호", 
                "Su": "물리적 강화", "Hu": "기계적 수행", "Ru": "불규칙", "Lu": "명확", "Vu": "불안정"
            }

    def _recursive_join(self, item):
            if item is None: return ""
            if isinstance(item, list): return "".join([self._recursive_join(i) for i in item])
            if isinstance(item, Tree): return "".join([self._recursive_join(child) for child in item.children])
            
            if isinstance(item, Token):
                t = str(item).strip()
                if t in ["@", "eth"]: return ""
                if t == "!": return " [경고]"

                # 1. 시간 태그 처리 (T1800 등)
                if t.startswith('T') and t[1:].isdigit() and len(t) >= 5:
                    return f"{t[1:3]}시 {t[3:5]}분 "
                # 단독 T 처리 (뒤에 숫자가 붙을 예정인 경우)
                if t == "T": return "시간"

                # 2. 복합 태그 분해 (재귀적 심층 분해)
                # 사전의 키를 긴 순서대로 검사하여 부분 일치를 찾음
                for tag_key in sorted(self.dict_map.keys(), key=len, reverse=True):
                    if t.startswith(tag_key):
                        prefix_val = self.dict_map[tag_key]
                        remain = t[len(tag_key):]
                        if not remain:
                            return prefix_val
                        # 남은 부분(Mu 등)이 있으면 다시 재귀적으로 번역해서 합침
                        return prefix_val + self._recursive_join(Token('INNER', remain))

                # 3. 확정/가변 접미사 처리
                for suffix in ["ic", "ec"]:
                    if t.endswith(suffix) and t[:-2] in self.dict_map:
                        return f"{self.dict_map[t[:-2]]}({self.dict_map[suffix]})"
                
                return self.dict_map.get(t, t)
            return str(item)

    def tag_content(self, items):
        # 1. 모든 아이템을 먼저 번역함
        translated_items = [self._recursive_join(i) for i in items]
        
        # 2. 만약 첫 번째 아이템이 "시간"이라면 뒤의 숫자를 가로채서 합침
        if translated_items[0] == "시간" and len(items) > 1:
            num_part = str(items[1])
            if num_part.isdigit() and len(num_part) >= 4:
                res = f"{num_part[:2]}시 {num_part[2:4]}분 "
                # 시간으로 합쳤으므로 나머지 요소(vector_suffix 등)만 붙임
                for i in items[2:]:
                    res += self._recursive_join(i)
                return res

        # 3. 일반적인 태그 처리 (숫자가 속성으로 해석되는 경우)
        res = translated_items[0]
        num_str, vec_str, desc_str = "", "", ""
        
        for i_idx, i in enumerate(items[1:], 1):
            if isinstance(i, Token) and i.type == "NUMBER":
                n = str(i)
                # 속성 숫자로 해석 (d/v)
                d = {"1":"10분미만", "2":"30분미만", "3":"1시간미만", "4":"3시간미만", "5":"3시간이상"}.get(n[0], "미정")
                v = {"1":"안정", "2":"약간불안", "3":"불안정", "4":"빠름", "5":"매우빠름"}.get(n[1] if len(n)>1 else "1", "안정")
                num_str = f"({d}/{v})"
            elif isinstance(i, Tree) and i.data == "vector_suffix":
                vec_str = self.vector_suffix(i.children)
            else:
                desc_str += translated_items[i_idx]
                
        return f"{res}{num_str}{vec_str}{desc_str}"

    def vector_suffix(self, items):
        kind = self.dict_map.get(str(items[0]), str(items[0]))
        num_str = ""
        for i in items:
            if isinstance(i, Token) and i.type == "NUMBER":
                n = str(i)
                d = {"1":"10분미만", "2":"30분미만", "3":"1시간미만", "4":"3시간미만", "5":"3시간이상"}.get(n[0], "미정")
                v = {"1":"안정", "2":"약간불안", "3":"불안정", "4":"빠름", "5":"매우빠름"}.get(n[1] if len(n)>1 else "1", "안정")
                num_str = f"({d}/{v})"
        return f"{kind}{num_str}"

    def logic_group(self, items): return f"{{{self._recursive_join(items)}}}"
    def action_group(self, items): return f"[{self._recursive_join(items)}]"
    def inner_group(self, items): return f"({self._recursive_join(items)})"
    def atom(self, items): return self._recursive_join(items)

    def target(self, items):
            # "대상: 대학교" -> "대학교(으)로 향함" 또는 "대학교를 대상으로 함"
            val = self._recursive_join(items)
            return f" {Josa(val, '을/를')} 대상으로 "

    def eth_property(self, items): return f" (성격: {self._recursive_join(items)})"
    def causal_expr(self, items):
            l, r = self._recursive_join(items[0]), self._recursive_join(items[2])
            # "A => B" -> "A하면 B하게 된다"
            op = "a'" in str(items[1])
            symbol = "하게 되며, 이로 인해 " if op else "하고 나서 "
            return f"{l}{symbol}{r}"
    def sequence_expr(self, items):
        l, r = self._recursive_join(items[0]), self._recursive_join(items[2])
        return f"{l} + {r}" if str(items[1]) == "en" else f"{l}, {r}"
    def expressions(self, items): return "\n".join([self._recursive_join(i).strip() for i in items if i])
    def start(self, items):
            res = self._recursive_join(items)
            # 마지막에 마침표를 찍어 문장 완성
            if not res.endswith(('.', '?', '!')):
                res += "함."
            return res

# 실행 및 테스트
parser = Lark(my_grammar, start='start', parser='earley')
translator = LangTranslator()

test_cases = [
    "{ImAegend @Eceaf}~ a'{ImAemend @Ym}, Tn, Ym,ImAusi"
]

print("## 복합 태그 보정 번역 결과 ##\n")
for code in test_cases:
    try:
        tree = parser.parse(code)
        print(f"입력: {code}\n번역: {translator.transform(tree)}\n")
    except Exception as e:
        print(f"오류: {e}")
