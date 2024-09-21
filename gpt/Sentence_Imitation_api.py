from api_request import call_llm_api
import re
def sentence_imitation(sentences,chains):
    prompt_template =  """假设一个金融语言模型能够自动分析用户问题，提取关键内容和逻辑链，并在数据库中匹配相应的句子以生成回答。现有用户问题已通过以下句子匹配：{0}。首先，请识别这些句子涉及的行业和包含的金融要素。然后，基于这些行业信息、金融要素及句子中的逻辑链，重构一个新的句子。这个新句子应整合所有相关内容而不引入额外信息，并确保所包含的逻辑链仅来源于提供的逻辑链。最后，请输出这个句子及其完整的逻辑链，按字典格式输出：{{'sentence':'{{}}', 'chains': {{}}}}。注意：回答须用中文且直接相关，只输出仿写的句子和逻辑链即可，不需要输出行业和金融要素，生成的逻辑链格式为{{"A":,"关系":,"B":}}，不得包含非必要文本。"""
    prompt = prompt_template.format(sentences, chains)
    api_key = "sk-QeiIJwcjqnhybuSeBbC0F27eEc0b42529a4410194b362bBb"
    response = call_llm_api(prompt,api_key,temperature=0.2)
    pattern = r"({)(.*)(})"
    match = re.search(pattern,response,re.DOTALL)
    if match:
        result = match.group()
        result = re.sub("，",",",result)
        temp = eval(result)
        return temp["sentence"],temp["chains"]
    else:
        sentence_imitation(sentences,chains)

if  __name__ == '__main__':
    sentence = [
    "上半年次高端白酒内部业绩表现分化。今年春节期间，虽然疫情管控已全面放开，但由于商务宴席消费场景仍有缺失，次高端白酒春节表现偏弱，部分经销商仍在消化去年四季度的库存，复苏节奏相对滞后，内部表现分化",
    "区域白酒今年上半年业绩良性增长。受益于春节返乡、走亲送礼等因素催化，区域白酒动销得到明显提振，2023Q1业绩表现整体较好",
    "次高端白酒业绩表现分化，静待动销改善。结构升级与产品推新推动次高端白酒发展。次高端白酒积极扩产，加大业务区域布局以提高市场影响力。",
    "产品提价不及预期。渠道扩张不及预期。新品推广不及预期。动销不及预期。行业竞争加剧。宏观经济下行风险。"
    ] 
    chain = [
    {"A": "次高端白酒", "关系": "因果", "B": "商务宴席减少和库存积压"},
    {"A": "商务宴席减少和库存积压", "关系": "因果", "B": "复苏缓慢"},
    {"A": "区域白酒", "关系": "因果", "B": "春节返乡和赠礼需求增强"},
    {"A": "春节返乡和赠礼需求增强", "关系": "因果", "B": "业绩提升"},
    {"A": "结构升级和新品推广", "关系": "因果", "B": "预期未达"},
    {"A": "市场竞争激烈", "关系": "因果", "B": "业绩下行风险"},
    {"A": "宏观经济下行", "关系": "因果", "B": "业绩下行风险"}
    ]
    result = sentence_imitation(sentence,chain)
    