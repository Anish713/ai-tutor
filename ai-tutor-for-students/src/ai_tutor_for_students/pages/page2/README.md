# Mixture-of-Agents

## Features

- Interactive chat interface powered by MOA
- Configurable main model and layer agents
- Real-time streaming of responses
- Visualization of intermediate layer outputs
- Customizable agent parameters through the UI


## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Use the sidebar to configure the MOA settings:
   - Select the main model
   - Set the number of cycles
   - Customize the layer agent configuration

4. Start chatting with the MOA system using the input box at the bottom of the page.

## Project Structure

- `app.py`: Main Streamlit application file
- `moa/`: Package containing the MOA implementation
  - `__init__.py`: Package initializer
  - `moa.py`: Core MOA agent implementation
  - `prompts.py`: System prompts for the agents
- `main.py`: CLI version of the MOA chat interface
- `requirements.txt`: List of Python dependencies
- `static/`: Directory for static assets (images, etc.)

## Configuration

The MOA system can be configured through the Streamlit UI or by modifying the default configuration in `app.py`. The main configurable parameters are:

- Main model: The primary language model used for generating final responses
- Number of cycles: How many times the layer agents are invoked before the main agent
- Layer agent configuration: A JSON object defining the system prompts, model names, and other parameters for each layer agent
