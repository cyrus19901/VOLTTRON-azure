export SOURCE=pnnl/lightcontrolagent/
export CONFIG=pnnl/lightcontrolagent/config
export TAG=lightcontrolagent

./scripts/core/make-agent.sh

# To set the agent to autostart with the platform, pass "enable"
# to make-agent.sh: ./scripts/core/make-agent.sh enable

