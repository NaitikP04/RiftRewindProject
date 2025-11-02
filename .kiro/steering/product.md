# Product Overview

Rift Rewind is an AI-powered League of Legends match analysis tool that generates personalized year-end reviews in a Spotify Wrapped style. The application analyzes player match history and performance data to create engaging, data-driven summaries of their gaming year.

## Core Features

- **AI-Powered Year Review**: LangChain agent using Claude 3.5 Sonnet via AWS Bedrock
- **Smart Match Fetching**: Prioritizes ranked matches for competitive insights (50-200 matches analyzed)
- **Comprehensive Analysis**: KDA trends, champion pool, playstyle personality, performance improvement tracking
- **Retry-Safe Architecture**: Handles both Riot API and Bedrock rate limits with intelligent caching
- **Multi-stage Pipeline**: Match fetching → Data enrichment → AI synthesis → Structured output

## Target Users

- League of Legends players seeking insights into their performance
- Players wanting shareable year-end summaries of their gaming achievements
- Competitive players looking for data-driven improvement suggestions

## Key Value Propositions

1. **Personalized Insights**: Tailored analysis based on individual play patterns
2. **Performance Tracking**: Clear trends showing improvement or areas needing work
3. **Engaging Format**: Fun, shareable content similar to popular year-end summaries
4. **Actionable Feedback**: Specific recommendations for gameplay improvement

### Planned Features (Next Phase)
- **Profile Dashboard**: Rank display, summoner icon, live challenges, unique stat highlight
- **Card-Based Review**: Modular components for champion mastery, stat highlights, coaching insights
- **Timeline Analysis**: Individual game breakdown with critical moments and decision points
- **OPGG MCP Integration**: Meta build comparison, high-elo benchmarking
- **Interactive Visualizations**: Rank progression, champion mastery curves, stat improvements
- **Clip Integration**: Highlight moments with AI-generated commentary (stretch goal)

## Analysis Quality Focus

**What Makes Our Insights Unique:**
1. **Context-Aware Coaching**: AI understands meta, champion matchups, and role-specific expectations
2. **Granular Data**: Uses Riot's challenge system + timeline data for precise analysis
3. **Actionable Recommendations**: Specific advice (e.g., "Your vision score drops by 40% after 20 minutes")
4. **Comparative Benchmarks**: Your stats vs. pro builds, meta trends, and rank expectations
5. **Personalized Narrative**: Adapts tone and depth based on play frequency and skill level
