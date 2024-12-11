# SportsStats
A python application and Postgres database to retrieve team statistics for the NHL, NBA, and MLB. 

## Tables and Fields
Tables are Leagues, Teams, Seasons, and Standings. Fields and relationships are outlined as per the ERD below.  
<img width="927" alt="Screenshot 2024-12-11 at 1 13 47 PM" src="https://github.com/user-attachments/assets/407ec0b7-eaa6-44c1-bb82-afeebc2359fe" />

## Resources
Data was sourced from the following APIs and python wrappers:
**- MLB:** MLB data was retrieved from the [MLB-StatsAPI Python Wrapper](https://pypi.org/project/MLB-StatsAPI/). Data for the Seasons table with dates for the regular season, spring training, and postseason was retrieved from the `statsapi.get('seasons')` function. Data for the Leagues, Teams, and Standings tables was retrieved from `statsapi.standings_data` function. 
**- NBA:** NBA data for the Leagues, Teams, and Standings tables was retrieved from the [NBA API](https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguestandings.md) Admittedly, finding the correct headers to get this API to work was a challenge. Data for the Seasons table was added manually, and is something I would change in the future.
**- NHL:** NHL data for the Seasons, and Leagues tables was retrieved from the [NHL API](https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#nhl-stats-api-documentation) using the `https://api.nhle.com/stats/rest/season` endpoint . Data for the Teams and Standings table was retrieved from the [Sports Radar API](https://developer.sportradar.com/ice-hockey/reference/nhl-overview).

## Next Steps
As I continue to develop this repository, I want to implement several changes to ensure the code remains functional, maintainable, and capable of retrieving and processing data consistently and reproducibly. Below are some initial areas of focus:

NBA Seasons: The seasonal dates were manually added, so I plan to review the API and its documentation to identify opportunities for automating the retrieval of seasonal date data. This will help ensure accuracy and reduce manual interferance.

NHL Standings and Teams Tables: Currently, standings data is retrieved indirectly through Sports Radar. I will evaluate the NHL API to determine whether it provides a direct and more efficient method for accessing this data, potentially improving both performance and reliability.

Code Standardization and Cleaning: I plan to refactor the codebase to improve standardization and maintainability. Specifically,  I want to ensure that functions within each class follow consistent design principles and operate on uniform data structures. For better organization, I will introduce a high-level dictionary structure at the top of each repective class to store key datasets for `league_data`, `seasons_data`, `teams_data`, and `standings_data`. These dictionaries will include nested dictionaries for each league. Overall, my goal is to enhance code readability and scalability while keeping in mind object-oriented programming best practices.


