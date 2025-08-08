const basePath = import.meta.env.BASE_URL || "./";

export async function fetchCompanies() {
  const res = await fetch(`${basePath}data/companies.json`);
  return res.json();
}

export async function fetchCompanyData(slug) {
  const res = await fetch(`${basePath}data/${slug}.json`);
  return res.json();
}