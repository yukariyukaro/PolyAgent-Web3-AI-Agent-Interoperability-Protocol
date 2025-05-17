import { AINews, Errors } from "@chaingpt/ainews";

const ainews = new AINews({ apiKey: process.env.CHAINGPT_API_KEY! });

async function main() {
  try {
    // sdk doc: https://docs.chaingpt.org/dev-docs-b2b-saas-api-and-sdk/ai-crypto-news-api-and-sdk-and-rss/sdk-reference
    const response = await ainews.getNews({
      categoryId: [5],              // DeFi category
      subCategoryId: [15],          // Ethereum sub-category
      fetchAfter: new Date('2024-01-01'),
      searchQuery: "funding",       // search keyword in title/description
      limit: 10,                    // up to 10 results
      offset: 0,                    // start from the first result
      sortBy: 'createdAt'           // sort by newest
    });
    for (const article of response.data) {
      console.log(article);
    }
  } catch (error) {
    console.error("Error fetching news:", error);
  }
}

main();