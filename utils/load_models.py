



def load_model(llm_type):
    existed = {
        "chatglm6b":load_chatglm6b
    }
    return existed[llm_type]()

def load_chatglm6b():
    from transformers import AutoModel,AutoTokenizer
    