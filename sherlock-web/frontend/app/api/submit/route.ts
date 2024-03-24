export async function POST(req: Request) {
    const data = await req.json();

    const { username, sites, withNSFW } = data;

    const f = [];

    if (withNSFW)
        f.push("nsfw");

    return await fetch("http://api:8000", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            usernames: [username],
            sites,
            f
        })
    });
}