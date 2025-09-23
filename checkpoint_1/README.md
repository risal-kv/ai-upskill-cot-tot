# ReAct Agent Learning Project - Checkpoint 1

A hands-on project to learn how to build a ReAct (Reasoning and Acting) agent. This checkpoint will guide you through creating an intelligent agent that can reason through problems and take actions step by step.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.11** installed on your system
- An **OpenAI API key** (we'll set this up in the setup guide below)

## Quick Setup Guide

Follow these simple steps to get started:

1. **Navigate to the checkpoint_1 directory:**

   ```bash
   cd ai-upskill-cot-tot/checkpoint_1
   ```

2. **Create and activate a virtual environment:**

   **Option A: Using conda (if you have conda installed)**

   ```bash
   # Create conda environment
   conda create -n venv python=3.11

   # Activate conda environment
   conda activate venv
   ```

   **Option B: Using venv (if you don't have conda)**

   ```bash
   # Create virtual environment
   python3.11 -m venv venv

   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**

   Create a `.env` file in the checkpoint_1 directory:

   ```bash
   # Create .env file
   touch .env
   ```

   Add your OpenAI API key to the `.env` file:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   **Note:** You can also copy the sample environment file from the parent directory:
   ```bash
   cp ../env_sample .env
   ```
   Then edit the `.env` file to add your actual API key.

   **To get an OpenAI API key:**

   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Sign up or log in to your account
   - Click "Create new secret key"
   - Copy the key and paste it in your `.env` file

5. **Run the application:**

   ```bash
   streamlit run app.py
   ```

6. **Open your browser:**
   - Go to `http://localhost:8501`
   - Select "agent" from the dropdown menu in the left sidebar
   - Start building your AI agent!

## Prerequisites Confirmation

After running the application, you should see an interface similar to this:

The interface should show:

- A left sidebar with settings and data tables (Orders and Shipments)
- A chat interface on the right with sample conversation
- Dropdown menus for agent and user selection
- Pre-populated data in the tables

## What You'll Learn

This project will teach you:

- How AI agents think and make decisions
- How to build tools that agents can use
- How to create interactive web interfaces for your agents
- How to handle different types of user questions

## Sample Queries

Once your agent is set up, you can ask questions like:

- "Where is my order #1234?"
- "What's the status of order #1235?"
- "Tell me about shipment #1001"
- "Is order #1236 delivered?"
- "Show me all orders for customer 1001"
- "What orders did customer 1001 place in September 2025?"

## How It Works

1. **User Input**: User enters a question in the Streamlit interface
2. **Agent Reasoning**: The ReAct agent analyzes the question and decides what action to take
3. **Tool Execution**: Agent calls appropriate tools (get_order, get_shipment, etc.)
4. **Observation**: Agent processes the tool results
5. **Iteration**: Agent continues reasoning until it has enough information
6. **Final Answer**: Agent provides a complete, grounded answer

## Architecture

- **tools.py**: Defines Pydantic schemas and tool functions
- **agent.py**: Implements the ReAct agent with LangChain integration
- **app.py**: Provides the Streamlit web interface
- **prompt.py**: Contains prompt templates and configurations
- **agent_checkpoints/**: Contains different agent implementations (CoT and ReAct)

## Project Structure

```
checkpoint_1/
├── app.py                    # Streamlit web interface for your agent
├── agent.py                  # Main AI agent implementation
├── tools.py                  # Tools your agent can use
├── prompt.py                 # Prompt templates and configurations
├── requirements.txt          # Python packages needed
├── README.md                 # This guide
└── agent_checkpoints/        # Different agent implementations
    ├── __init__.py
    ├── cot_checkpoint.py     # Chain of Thought agent
    └── react_checkpoint.py   # ReAct agent
```

## Getting Started

This checkpoint includes implementations of both Chain of Thought (CoT) and ReAct agents. As you explore this checkpoint, you'll:

- Understand how different reasoning patterns work (CoT vs ReAct)
- Learn to build tools that agents can use
- Explore prompt engineering techniques
- See how agents make decisions and take actions
- Build interactive interfaces for your agents

The `agent_checkpoints/` directory contains different agent implementations that you can compare and learn from.

## Need Help?

If you run into any issues:

1. Make sure you're using Python 3.11
2. Check that your virtual environment is activated
3. Verify your `.env` file has the correct API key
4. Ensure all dependencies are installed with `pip install -r requirements.txt`
