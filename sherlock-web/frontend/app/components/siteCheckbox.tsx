"use client"
import { Checkbox, Grid, Tooltip } from "@mui/joy"
import { ChangeEvent } from "react";

type props = {
    name: string,
    url: string,
    checked: boolean | undefined,
    onChange: (value: boolean) => void,
    required: boolean,
}

export default function SiteCheckBox({name, url, checked, onChange, required}: props) {
    const change = (e: ChangeEvent<HTMLInputElement>) => onChange(e.target.checked);

    return (
        <Grid xs={2} sm={2} md={2} lg={2} >
            <Tooltip title={url}>
                <Checkbox 
                    name={"site["+name+"]"} 
                    label={name}
                    checked={checked} 
                    onChange={change}
                    required={required}
                />
            </Tooltip>
        </Grid>
    );
}