"""Toolset for accessing alphahold database for bulk downloads and possibly more"""

import argparse
import asyncio
from pprint import pprint
from ftplib import FTP

import httpx

# TODO implement with aioftp so everything is async


class AFDB:
    """
    TODO
    """

    def __init__(
        self,
        ftp_server: str = "ftp.ebi.ac.uk",
        version: str = "latest",
    ) -> None:
        """TODO"""
        self.ftp_server = ftp_server
        self.version = version
        self.api_client = httpx.AsyncClient()

    async def get_readme(self) -> str:
        """TODO"""
        try:
            request_readme = await self.api_client.get(
                f"https://{self.ftp_server}/pub/databases/alphafold/README.txt"
            )
            request_readme.raise_for_status()
            await self.api_client.aclose()
        except httpx.HTTPStatusError as err:
            return f"Exception occured for fetching the README. {err}"
        except httpx.RequestError as err:
            return f"Error occurred during the request: {err}"
        return request_readme.text

    async def get_metadata_json(self) -> dict | str:
        """TODO"""
        try:
            request_metadata = await self.api_client.get(
                f"https://{self.ftp_server}/pub/databases/alphafold/download_metadata.json"
            )
            request_metadata.raise_for_status()
            await self.api_client.aclose()
        except httpx.HTTPStatusError as err:
            return f"Exception occured for fetching the README. {err}"
        except httpx.RequestError as err:
            return f"Error occurred during the request: {err}"
        return request_metadata.json()

    def list_accessions(self) -> list[str]:
        """TODO"""
        directories = []
        with FTP("ftp.ebi.ac.uk") as ftp:
            ftp.login()
            ftp.cwd(f"/pub/databases/alphafold/{self.version}/")
            directories = ftp.nlst()
        return directories


async def main():
    """TODO"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="Get the metadata from alphafold, the list contains all the archive files available for bulk download.",
    )
    parser.add_argument(
        "-r",
        "--readme",
        action="store_true",
        help="Get the readme from alphahold ftp server",
    )
    parser.add_argument(
        "-ls",
        "--list_acs",
        action="store_true",
        help="List accessions from the ftp server",
    )
    # TODO add a way to setup version
    afdb = AFDB()
    args = parser.parse_args()
    if args.metadata:
        pprint(await afdb.get_metadata_json())
    elif args.readme:
        print(await afdb.get_readme())
    elif args.list_acs:
        for accession in afdb.list_accessions():
            if accession.startswith("UP"):
                print(accession)


if __name__ == "__main__":
    asyncio.run(main())
