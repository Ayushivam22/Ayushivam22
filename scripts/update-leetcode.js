import fs from 'fs';

const LEETCODE_USERNAME = 'YOUR_LEETCODE_USERNAME'; // <-- Replace with your handle

const GRAPHQL_QUERY = `
query getUserActivity($username: String!) {
  matchedUser(username: $username) {
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
  recentAcSubmissionList(username: $username, limit: 5) {
    title
    titleSlug
    timestamp
  }
}
`;

async function fetchLeetCodeData() {
  const response = await fetch('https://leetcode.com/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Referer': 'https://leetcode.com',
    },
    body: JSON.stringify({
      query: GRAPHQL_QUERY,
      variables: { username: LEETCODE_USERNAME },
    }),
  });

  const { data } = await response.json();
  return data;
}

async function updateReadme() {
  try {
    const data = await fetchLeetCodeData();

    if (!data?.matchedUser) {
      throw new Error('Failed to retrieve user data. Verify the username.');
    }

    const stats = data.matchedUser.submitStatsGlobal.acSubmissionNum;
    const totalSolved = stats.find(s => s.difficulty === 'All')?.count || 0;
    const easySolved = stats.find(s => s.difficulty === 'Easy')?.count || 0;
    const mediumSolved = stats.find(s => s.difficulty === 'Medium')?.count || 0;
    const hardSolved = stats.find(s => s.difficulty === 'Hard')?.count || 0;

    const recentSubmissions = data.recentAcSubmissionList || [];

    const statsTable = `| Total Solved | Easy | Medium | Hard |
| :--- | :--- | :--- | :--- |
| **${totalSolved}** | ${easySolved} | ${mediumSolved} | ${hardSolved} |`;

    const recentList = recentSubmissions.length > 0
      ? recentSubmissions
          .map(sub => {
            const date = new Date(parseInt(sub.timestamp) * 1000).toISOString().split('T')[0];
            return `- [${sub.title}](https://leetcode.com/problems/${sub.titleSlug}/) — *${date}*`;
          })
          .join('\n')
      : '- *No recent submissions found.*';

    const generatedContent = `<!-- LEETCODE:START -->
#### Problem Solving Stats
${statsTable}

#### Recently Solved Problems
${recentList}
<!-- LEETCODE:END -->`;

    const readmePath = 'README.md';
    let readme = fs.readFileSync(readmePath, 'utf-8');

    const regex = /<!-- LEETCODE:START -->[\s\S]*<!-- LEETCODE:END -->/;
    readme = readme.replace(regex, generatedContent);

    fs.writeFileSync(readmePath, readme);
    console.log('README successfully updated with LeetCode activity.');
  } catch (error) {
    console.error('Error updating README:', error);
    process.exit(1);
  }
}

updateReadme();