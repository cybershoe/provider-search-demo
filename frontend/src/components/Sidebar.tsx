import { PropsWithChildren, DetailedHTMLProps } from 'react'

interface SidebarButtonProps {
    onClick: () => void;
    expanded?: boolean;
}

interface SidebarProps extends PropsWithChildren {
    expanded: boolean,
    width: number,
    className?: string
}

export function SidebarButton({ onClick, expanded = false }: SidebarButtonProps) {
    return (
        <div
            className='button'
            onClick={onClick}>
            <p>{expanded ? ">>" : "<<"}</p>
        </div>
    )
}

export function Sidebar({ expanded, width, children, ...rest }: SidebarProps) {
    return (
        <div
            {...rest}
            style={{
                // display: expanded ? "block" : "none",
                width: expanded ? width : 0,
            }}>

            {children}
        </div>
    )
}
