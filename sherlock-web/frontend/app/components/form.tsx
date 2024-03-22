"use client"
import { Grid, Input, Divider, Stack, Checkbox, Button } from "@mui/joy";

import SiteCheckbox from "./siteCheckbox";

import * as data from "../../data.json";
import { ChangeEvent, FormEvent, useState } from "react";

type pageList = {
    name: string,
    url: string
}[];

let sites: pageList = [];
let sitesWithNSFW: pageList = [];

const checkedSitesDefault: Record<string, boolean> = {};

for (const [name, values] of Object.entries(data)) {
    const {url, isNSFW} = values as any;

    const parsedData = {name, url};

    sitesWithNSFW.push(parsedData);

    checkedSitesDefault[name] = true;
    
    if (!isNSFW) 
        sites.push(parsedData)    
}

export default function Form() {
    const [withNSFW, setWithNSFW] = useState(false);
    const [loading, setLoading] = useState(false);

    const [checkedSites, setCheckedSites] = useState(checkedSitesDefault);

    const clickNSFW = (e: ChangeEvent<HTMLInputElement>) => setWithNSFW(e.target.checked);

    const clickCheckAll = (e: ChangeEvent<HTMLInputElement>) => {
        const {checked} = e.target;

        let newCheckedSites = {...checkedSites};
        for (let key in checkedSites)
            newCheckedSites[key] = checked;

        setCheckedSites(newCheckedSites);
    };

    const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        setLoading(true);

        const response = await fetch("/api/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: e.currentTarget.username.value,
                sites: Object.entries(checkedSites).filter(([_, value]) => value).map(([key, _]) => key)
            })
        });
    };

    const currentSite = withNSFW ? sitesWithNSFW : sites;

    const required = !Object.values(checkedSites).some(value => value);

    return (
        <form style={{ height: "95%"}} onSubmit={onSubmit}>
            <Stack direction="column" spacing={2} sx={{height: "100%"}}>
                <Input name="username" required />

                <Divider>
                    <Stack direction="row" spacing={3}>
                        <Checkbox label="With NSFW" onChange={clickNSFW} />
                        <Checkbox label="Check All" onChange={clickCheckAll} />
                    </Stack>
                </Divider>

                <Grid container spacing={2}  columns={{ xs: 4, sm: 6, md: 8, lg: 10, xl: 12 }} sx={{maxHeight: "100%", overflow: "auto"}} flexGrow={1}>
                    {currentSite.map(
                        ({name, url}) => {
                            const change = (value: boolean) => setCheckedSites({
                                ...checkedSites,
                                [name]: value
                            });

                            return (
                                <SiteCheckbox 
                                    name={name}
                                    url={url} 
                                    key={"site-"+name}
                                    checked={checkedSites[name]}
                                    onChange={change}
                                    required={required}
                                />
                            );
                        }
                    )}
                </Grid>

                <Button type="submit" loading={loading}>Send</Button>
            </Stack>
        </form>
    );
}

