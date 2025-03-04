from website import create_app
import numpy as np
from computations import initialize_scores, load_embeddings
from text_generation import init_genai
import pandas as pd

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)