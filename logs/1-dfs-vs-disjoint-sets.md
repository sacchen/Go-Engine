# DFS for Go group capture
#### 4-23-2025

Past few days, I:
- Wrote initial game logic and displaying to console
- Refactored into two classes for board and console_ui
- Wrote beginning of get_groups_and_liberties

### DFS vs disjoint sets
I debugged Depth First Search with Flood fill today, which determines what stones form a group and how many liberties the group has. A group of stones is a connection of same-colored stones that are top-bottom-right-left of each other. Liberties are the number of empty spaces surrounding a group, or the number of stones it would take to capture a group. So tracking groups and liberties is important to ensuring legal moves and capturing.

I considered two approaches for identifying groups of stones: Depth First Search and Disjoint Sets. My initial intuition was to use disjoint sets. Finding out which nodes are part of the same group and checking adjacent nodes was an intuitive idea for me because my DSA class used disjoint sets to check adjacent cells and connect cells together to generate mazes.

My DSA class actually introduced DFS two days ago - the same day I was deciding on how to implement groups and liberties. I settled on DFS because it would be easier to reason about and give me practice for a new algorithm. I was surprised to learn that disjoint sets is actually the optimal way because you get n lookup time and avoids recomputing groups every time you place a move or capture. However, using disjoint sets would be harder to implement because you would have to be very careful about checking the adjacent nodes and updating the groups when capturing happens. I knew checking the adjacent nodes would be difficult because it was challenging during the maze generation assignment, so I picked DFS.

### Next steps
- implementing the capturing logic and testing to see if it works
- making the basic bot that chooses random moves

### Future decisions
- Chinese scoring
- 3 consecutive passes to end the game
- Ko rules