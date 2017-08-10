export SOURCE=pnnl/shadecontrolagent/
export CONFIG=pnnl/shadecontrolagent/config
export TAG=shadecontrolagent

./scripts/core/make-agent.sh

# To set the agent to autostart with the platform, pass "enable"
# to make-agent.sh: ./scripts/core/make-agent.sh enable

