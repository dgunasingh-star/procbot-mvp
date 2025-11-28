"""
Interactive Chat Interface for PROCBOT
Have real-time conversations with the Coordinator Agent
"""

from agents.coordinator_agent import create_coordinator_agent
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def main():
    """
    Run interactive chat session with the Coordinator Agent
    """
    # Create the agent
    print("Initializing PROCBOT Coordinator Agent...")
    coordinator = create_coordinator_agent()
    print("✓ Agent ready!\n")
    
    # Welcome message
    print("=" * 70)
    print("  PROCBOT - Interactive Procurement Assistant")
    print("=" * 70)
    print("\nWelcome! I'm your procurement coordinator assistant.")
    print("I can help you with:")
    print("  • Business case development")
    print("  • Requirements gathering")
    print("  • RFI/RFP management")
    print("  • Vendor evaluation")
    print("  • Executive summaries")
    print("\nType 'exit', 'quit', or 'bye' to end the conversation.")
    print("=" * 70)
    print()
    
    # Chat loop
    while True:
        try:
            # Get user input
            user_input = input("\n🧑 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Thank you for using PROCBOT! Goodbye!")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Get agent response
            print("\n🤖 PROCBOT: ", end="", flush=True)
            coordinator.print_response(user_input, stream=True)
            print()  # New line after response
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'exit' to quit.")

if __name__ == "__main__":
    main()
